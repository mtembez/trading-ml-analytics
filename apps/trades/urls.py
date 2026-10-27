from django.urls import path
from apps.trades.views import (
    AccountDetailView,
    AccountListCreateView,
    TradeDetailView,
    TradeListCreateView,
)

app_name = "trades"

urlpatterns = [
    path("", TradeListCreateView.as_view(), name="trade-list-create"),
    path("<uuid:pk>/", TradeDetailView.as_view(), name="trade-detail"),
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"),
    path("accounts/<uuid:pk>/", AccountDetailView.as_view(), name="account-detail"),
]
