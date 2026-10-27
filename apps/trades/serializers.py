from rest_framework import serializers
from apps.trades.models import Account, Trade


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class TradeSerializer(serializers.ModelSerializer):
    is_winner = serializers.BooleanField(read_only=True)

    class Meta:
        model = Trade
        fields = [
            "id",
            "account",
            "symbol",
            "asset_class",
            "position_type",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
            "quantity",
            "pnl",
            "pnl_percentage",
            "r_multiple",
            "emotional_state",
            "strategy",
            "status",
            "entry_time",
            "exit_time",
            "duration_minutes",
            "notes",
            "is_winner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "pnl", "pnl_percentage", "r_multiple", "duration_minutes", "created_at", "updated_at"]
