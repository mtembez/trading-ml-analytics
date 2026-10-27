from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Account(models.Model):
    """Trading account tracking cash balance, equity, and performance."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default="Primary Account")
    currency = models.CharField(max_length=10, default="USD")
    initial_balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("10000.00"))
    current_balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("10000.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (${self.current_balance})"


class Trade(models.Model):
    """Trading journal entry capturing financial variables and psychological/emotional states."""

    ASSET_FOREX = "forex"
    ASSET_CRYPTO = "crypto"
    ASSET_EQUITY = "equity"
    ASSET_COMMODITY = "commodity"
    ASSET_INDICES = "indices"

    ASSET_CHOICES = [
        (ASSET_FOREX, "Forex"),
        (ASSET_CRYPTO, "Crypto"),
        (ASSET_EQUITY, "Equity"),
        (ASSET_COMMODITY, "Commodity"),
        (ASSET_INDICES, "Indices"),
    ]

    POS_LONG = "LONG"
    POS_SHORT = "SHORT"
    POSITION_CHOICES = [
        (POS_LONG, "Long"),
        (POS_SHORT, "Short"),
    ]

    STATUS_OPEN = "OPEN"
    STATUS_CLOSED = "CLOSED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    EMOTION_DISCIPLINED = "disciplined"
    EMOTION_FOMO = "fomo"
    EMOTION_REVENGE = "revenge"
    EMOTION_HESITANT = "hesitant"
    EMOTION_GREEDY = "greedy"
    EMOTION_ANXIOUS = "anxious"
    EMOTION_BORED = "bored"

    EMOTIONAL_CHOICES = [
        (EMOTION_DISCIPLINED, "Disciplined"),
        (EMOTION_FOMO, "FOMO"),
        (EMOTION_REVENGE, "Revenge"),
        (EMOTION_HESITANT, "Hesitant"),
        (EMOTION_GREEDY, "Greedy"),
        (EMOTION_ANXIOUS, "Anxious"),
        (EMOTION_BORED, "Bored"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="trades", null=True, blank=True)
    symbol = models.CharField(max_length=20, db_index=True)
    asset_class = models.CharField(max_length=20, choices=ASSET_CHOICES, default=ASSET_FOREX)
    position_type = models.CharField(max_length=10, choices=POSITION_CHOICES)
    
    entry_price = models.DecimalField(max_digits=16, decimal_places=6)
    exit_price = models.DecimalField(max_digits=16, decimal_places=6, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=16, decimal_places=6)
    take_profit = models.DecimalField(max_digits=16, decimal_places=6, null=True, blank=True)
    quantity = models.DecimalField(max_digits=16, decimal_places=6)

    pnl = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    pnl_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    r_multiple = models.FloatField(null=True, blank=True)

    emotional_state = models.CharField(
        max_length=20,
        choices=EMOTIONAL_CHOICES,
        default=EMOTION_DISCIPLINED,
        db_index=True,
    )
    strategy = models.CharField(max_length=50, default="trend_following")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_CLOSED, db_index=True)

    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-entry_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(entry_price__gt=0),
                name="trade_entry_price_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="trade_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(stop_loss__gt=0),
                name="trade_stop_loss_positive",
            ),
        ]

    def clean(self):
        super().clean()
        if self.entry_price is not None and self.stop_loss is not None:
            if self.position_type == self.POS_LONG and self.stop_loss >= self.entry_price:
                raise ValidationError({"stop_loss": "For LONG positions, stop loss must be strictly below entry price."})
            elif self.position_type == self.POS_SHORT and self.stop_loss <= self.entry_price:
                raise ValidationError({"stop_loss": "For SHORT positions, stop loss must be strictly above entry price."})

    def save(self, *args, **kwargs):
        self.clean()
        # Compute metrics if trade is closed and has exit price
        if self.status == self.STATUS_CLOSED and self.exit_price is not None:
            entry = self.entry_price
            exit_p = self.exit_price
            qty = self.quantity
            initial_risk_per_unit = abs(entry - self.stop_loss)

            if self.position_type == self.POS_LONG:
                raw_pnl = (exit_p - entry) * qty
                pct = ((exit_p - entry) / entry) * Decimal("100.0")
                r_mult = float((exit_p - entry) / initial_risk_per_unit) if initial_risk_per_unit > 0 else 0.0
            else:  # SHORT
                raw_pnl = (entry - exit_p) * qty
                pct = ((entry - exit_p) / entry) * Decimal("100.0")
                r_mult = float((entry - exit_p) / initial_risk_per_unit) if initial_risk_per_unit > 0 else 0.0

            self.pnl = round(raw_pnl, 2)
            self.pnl_percentage = round(pct, 2)
            self.r_multiple = round(r_mult, 2)

            if self.exit_time and self.entry_time:
                delta = self.exit_time - self.entry_time
                self.duration_minutes = max(0, int(delta.total_seconds() / 60))

        super().save(*args, **kwargs)

    @property
    def is_winner(self) -> bool:
        return self.pnl is not None and self.pnl > Decimal("0.00")

    def __str__(self):
        pnl_str = f"+${self.pnl}" if self.pnl and self.pnl > 0 else f"-${abs(self.pnl)}" if self.pnl else "OPEN"
        return f"{self.position_type} {self.symbol} ({self.emotional_state}) - {pnl_str}"
