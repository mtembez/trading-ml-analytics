from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from apps.trades.models import Account, Trade


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def account(db):
    return Account.objects.create(name="Apex Funded", initial_balance=Decimal("25000.00"), current_balance=Decimal("25000.00"))


class TestTradeModelsAndValidation:
    def test_long_trade_pnl_and_r_multiple_calculation(self, db, account):
        # Long trade: Entry = 100, SL = 95 (risk = 5), Exit = 115 (gain = 15), Qty = 10
        # PnL = (115 - 100) * 10 = +$150.00
        # R-Multiple = 15 / 5 = +3.0R
        trade = Trade.objects.create(
            account=account,
            symbol="AAPL",
            asset_class=Trade.ASSET_EQUITY,
            position_type=Trade.POS_LONG,
            entry_price=Decimal("100.00"),
            stop_loss=Decimal("95.00"),
            exit_price=Decimal("115.00"),
            quantity=Decimal("10.00"),
            emotional_state=Trade.EMOTION_DISCIPLINED,
            status=Trade.STATUS_CLOSED,
            entry_time=timezone.now(),
            exit_time=timezone.now(),
        )
        assert trade.pnl == Decimal("150.00")
        assert trade.pnl_percentage == Decimal("15.00")
        assert trade.r_multiple == 3.0
        assert trade.is_winner is True

    def test_short_trade_pnl_and_r_multiple_calculation(self, db, account):
        # Short trade: Entry = 1.1000, SL = 1.1050 (risk = 0.0050), Exit = 1.0900 (gain = 0.0100), Qty = 100000
        # PnL = (1.1000 - 1.0900) * 100000 = +$1000.00
        # R-Multiple = 0.0100 / 0.0050 = +2.0R
        trade = Trade.objects.create(
            account=account,
            symbol="EURUSD",
            asset_class=Trade.ASSET_FOREX,
            position_type=Trade.POS_SHORT,
            entry_price=Decimal("1.1000"),
            stop_loss=Decimal("1.1050"),
            exit_price=Decimal("1.0900"),
            quantity=Decimal("100000"),
            emotional_state=Trade.EMOTION_DISCIPLINED,
            status=Trade.STATUS_CLOSED,
            entry_time=timezone.now(),
            exit_time=timezone.now(),
        )
        assert trade.pnl == Decimal("1000.00")
        assert trade.r_multiple == 2.0
        assert trade.is_winner is True

    def test_invalid_stop_loss_direction_raises_validation_error(self, db):
        # LONG with stop loss above entry price must fail
        with pytest.raises(ValidationError):
            Trade.objects.create(
                symbol="BTCUSDT",
                position_type=Trade.POS_LONG,
                entry_price=Decimal("50000.00"),
                stop_loss=Decimal("51000.00"),  # Invalid: above entry
                quantity=Decimal("0.5"),
            )

        # SHORT with stop loss below entry price must fail
        with pytest.raises(ValidationError):
            Trade.objects.create(
                symbol="BTCUSDT",
                position_type=Trade.POS_SHORT,
                entry_price=Decimal("50000.00"),
                stop_loss=Decimal("49000.00"),  # Invalid: below entry
                quantity=Decimal("0.5"),
            )

    def test_check_constraint_rejects_negative_entry_price(self, db):
        with pytest.raises((IntegrityError, ValidationError)):
            Trade.objects.create(
                symbol="FAIL",
                position_type=Trade.POS_LONG,
                entry_price=Decimal("-10.00"),
                stop_loss=Decimal("-20.00"),
                quantity=Decimal("1.0"),
            )

    def test_trade_list_and_create_api_endpoints(self, api_client, account):
        url = reverse("trades:trade-list-create")
        payload = {
            "account": str(account.id),
            "symbol": "GBPUSD",
            "asset_class": "forex",
            "position_type": "LONG",
            "entry_price": "1.250000",
            "stop_loss": "1.245000",
            "exit_price": "1.260000",
            "quantity": "50000",
            "emotional_state": "disciplined",
            "status": "CLOSED",
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["symbol"] == "GBPUSD"
        assert float(data["pnl"]) == 500.00
        assert float(data["r_multiple"]) == 2.0
        assert data["is_winner"] is True

        # Query with filter
        res_filter = api_client.get(url, {"symbol": "GBPUSD"})
        assert res_filter.status_code == status.HTTP_200_OK
        assert len(res_filter.json()) >= 1
