from decimal import Decimal
import pandas as pd
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from apps.analytics.engine import (
    compute_behavioral_matrix,
    compute_equity_series,
    compute_portfolio_metrics,
)
from apps.trades.models import Account, Trade


@pytest.fixture
def sample_trades_df():
    data = [
        {"entry_time": "2026-10-01 10:00:00", "pnl": 100.0, "r_multiple": 2.0, "emotional_state": "disciplined"},
        {"entry_time": "2026-10-02 11:00:00", "pnl": 100.0, "r_multiple": 2.0, "emotional_state": "disciplined"},
        {"entry_time": "2026-10-03 12:00:00", "pnl": -50.0, "r_multiple": -1.0, "emotional_state": "fomo"},
        {"entry_time": "2026-10-04 13:00:00", "pnl": 100.0, "r_multiple": 2.0, "emotional_state": "disciplined"},
        {"entry_time": "2026-10-05 14:00:00", "pnl": -50.0, "r_multiple": -1.0, "emotional_state": "revenge"},
        {"entry_time": "2026-10-06 15:00:00", "pnl": 100.0, "r_multiple": 2.0, "emotional_state": "disciplined"},
    ]
    return pd.DataFrame(data)


class TestVectorizedAnalyticsMath:
    def test_exact_portfolio_metrics_known_vectors(self, sample_trades_df):
        metrics = compute_portfolio_metrics(sample_trades_df, initial_capital=10000.0)

        assert metrics["total_trades"] == 6
        assert metrics["win_rate"] == 66.67
        assert metrics["gross_profit"] == 400.0
        assert metrics["gross_loss"] == 100.0
        assert metrics["net_pnl"] == 300.0
        assert metrics["profit_factor"] == 4.0
        assert metrics["final_equity"] == 10300.0
        assert metrics["avg_win"] == 100.0
        assert metrics["avg_loss"] == 50.0
        assert metrics["win_loss_ratio"] == 2.0
        assert metrics["expectancy_r"] == 1.0  # (2 + 2 - 1 + 2 - 1 + 2) / 6 = 6/6 = 1.0R
        assert metrics["sharpe_ratio"] > 0.0

    def test_empty_dataframe_defaults_gracefully(self):
        metrics = compute_portfolio_metrics(pd.DataFrame(), initial_capital=10000.0)
        assert metrics["total_trades"] == 0
        assert metrics["win_rate"] == 0.0
        assert metrics["final_equity"] == 10000.0
        assert metrics["profit_factor"] == 0.0

    def test_equity_curve_and_drawdown_series(self, sample_trades_df):
        series = compute_equity_series(sample_trades_df, initial_capital=10000.0)
        assert len(series) == 7  # Initial baseline + 6 trades
        assert series[0]["equity"] == 10000.0
        assert series[1]["equity"] == 10100.0
        assert series[2]["equity"] == 10200.0
        assert series[3]["equity"] == 10150.0
        assert series[3]["drawdown_pct"] > 0.0  # Drop from 10200 to 10150
        assert series[-1]["equity"] == 10300.0

    def test_behavioral_matrix_groups_by_emotion(self, sample_trades_df):
        matrix = compute_behavioral_matrix(sample_trades_df)
        assert len(matrix) == 3  # disciplined, fomo, revenge

        disciplined = next(m for m in matrix if m["emotional_state"] == "disciplined")
        assert disciplined["trade_count"] == 4
        assert disciplined["win_rate"] == 100.0
        assert disciplined["net_pnl"] == 400.0

        fomo = next(m for m in matrix if m["emotional_state"] == "fomo")
        assert fomo["trade_count"] == 1
        assert fomo["win_rate"] == 0.0
        assert fomo["net_pnl"] == -50.0

    def test_analytics_rest_endpoints(self, api_client, db):
        # Create a trade in database
        Trade.objects.create(
            symbol="EURUSD",
            position_type=Trade.POS_LONG,
            entry_price=Decimal("1.1000"),
            stop_loss=Decimal("1.0950"),
            exit_price=Decimal("1.1100"),
            quantity=Decimal("10000"),
            emotional_state=Trade.EMOTION_DISCIPLINED,
            status=Trade.STATUS_CLOSED,
            entry_time=timezone.now(),
            exit_time=timezone.now(),
        )

        res_overview = api_client.get(reverse("analytics:overview"))
        assert res_overview.status_code == status.HTTP_200_OK
        assert res_overview.json()["total_trades"] == 1
        assert res_overview.json()["win_rate"] == 100.0

        res_equity = api_client.get(reverse("analytics:equity-curve"))
        assert res_equity.status_code == status.HTTP_200_OK
        assert len(res_equity.json()) >= 2

        res_behavior = api_client.get(reverse("analytics:behavioral"))
        assert res_behavior.status_code == status.HTTP_200_OK
        assert len(res_behavior.json()) >= 1
