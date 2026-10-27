from rest_framework import generics, filters
from apps.trades.models import Account, Trade
from apps.trades.serializers import AccountSerializer, TradeSerializer


class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TradeListCreateView(generics.ListCreateAPIView):
    serializer_class = TradeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["symbol", "strategy", "notes"]
    ordering_fields = ["entry_time", "pnl", "r_multiple", "duration_minutes"]

    def get_queryset(self):
        qs = Trade.objects.all()
        symbol = self.request.query_params.get("symbol")
        asset_class = self.request.query_params.get("asset_class")
        emotional_state = self.request.query_params.get("emotional_state")
        status_val = self.request.query_params.get("status")

        if symbol:
            qs = qs.filter(symbol__iexact=symbol)
        if asset_class:
            qs = qs.filter(asset_class=asset_class)
        if emotional_state:
            qs = qs.filter(emotional_state=emotional_state)
        if status_val:
            qs = qs.filter(status=status_val)

        return qs


class TradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
