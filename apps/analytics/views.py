import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.analytics.engine import (
    compute_behavioral_matrix,
    compute_equity_series,
    compute_portfolio_metrics,
)
from apps.trades.models import Account, Trade


def get_trades_dataframe(account_id=None, symbol=None, asset_class=None):
    """Retrieve trades queryset and convert to pandas DataFrame."""
    qs = Trade.objects.filter(status=Trade.STATUS_CLOSED, exit_price__isnull=False)
    if account_id:
        qs = qs.filter(account_id=account_id)
    if symbol:
        qs = qs.filter(symbol__iexact=symbol)
    if asset_class:
        qs = qs.filter(asset_class=asset_class)

    data = list(qs.values(
        "id", "symbol", "asset_class", "position_type",
        "entry_price", "exit_price", "quantity", "pnl",
        "pnl_percentage", "r_multiple", "emotional_state",
        "strategy", "entry_time", "exit_time", "duration_minutes"
    ))
    return pd.DataFrame(data) if data else pd.DataFrame()


class OverviewAnalyticsView(APIView):
    """Compute aggregate portfolio metrics."""

    def get(self, request):
        account_id = request.query_params.get("account_id")
        symbol = request.query_params.get("symbol")
        asset_class = request.query_params.get("asset_class")
        initial_capital = float(request.query_params.get("initial_capital", 10000.0))

        df = get_trades_dataframe(account_id, symbol, asset_class)
        metrics = compute_portfolio_metrics(df, initial_capital=initial_capital)
        return Response(metrics, status=status.HTTP_200_OK)


class EquityCurveView(APIView):
    """Compute point-in-time equity curve and drawdown series."""

    def get(self, request):
        account_id = request.query_params.get("account_id")
        symbol = request.query_params.get("symbol")
        asset_class = request.query_params.get("asset_class")
        initial_capital = float(request.query_params.get("initial_capital", 10000.0))

        df = get_trades_dataframe(account_id, symbol, asset_class)
        series = compute_equity_series(df, initial_capital=initial_capital)
        return Response(series, status=status.HTTP_200_OK)


class BehavioralAnalyticsView(APIView):
    """Compute performance breakdown by psychological/emotional state."""

    def get(self, request):
        account_id = request.query_params.get("account_id")
        symbol = request.query_params.get("symbol")
        asset_class = request.query_params.get("asset_class")

        df = get_trades_dataframe(account_id, symbol, asset_class)
        matrix = compute_behavioral_matrix(df)
        return Response(matrix, status=status.HTTP_200_OK)
