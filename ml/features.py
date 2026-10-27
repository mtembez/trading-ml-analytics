"""Feature extraction and encoding pipeline for behavioral trading ML models."""

from typing import Any, Dict, List
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "planned_risk_reward",
    "emotional_bias_score",
    "is_long",
    "hour_of_day",
    "day_of_week",
    "rolling_win_rate",
    "consecutive_losses",
    "asset_class_code",
]

EMOTION_BIAS_MAP = {
    "disciplined": 0.0,
    "hesitant": 0.5,
    "bored": 0.8,
    "anxious": 1.0,
    "greedy": 1.6,
    "fomo": 2.2,
    "revenge": 3.0,
}

ASSET_CLASS_MAP = {
    "forex": 0.0,
    "crypto": 1.0,
    "equity": 2.0,
    "commodity": 3.0,
    "indices": 4.0,
}


def extract_trade_features(trade_input: Dict[str, Any]) -> Dict[str, float]:
    """Extract normalized numerical feature vector from pre-trade submission or trade record."""
    entry_price = float(trade_input.get("entry_price", 100.0))
    stop_loss = float(trade_input.get("stop_loss", 98.0))
    take_profit = float(trade_input.get("take_profit", 104.0)) if trade_input.get("take_profit") else (entry_price + 2.0 * abs(entry_price - stop_loss))

    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    planned_rr = (reward / risk) if risk > 0 else 1.0

    emotion = str(trade_input.get("emotional_state", "disciplined")).lower()
    bias_score = EMOTION_BIAS_MAP.get(emotion, 1.0)

    pos_type = str(trade_input.get("position_type", "LONG")).upper()
    is_long = 1.0 if pos_type == "LONG" else 0.0

    hour = float(trade_input.get("hour_of_day", 14.0))
    day = float(trade_input.get("day_of_week", 2.0))
    rolling_wr = float(trade_input.get("rolling_win_rate", 0.50))
    consecutive_losses = float(trade_input.get("consecutive_losses", 0.0))

    asset = str(trade_input.get("asset_class", "forex")).lower()
    asset_code = ASSET_CLASS_MAP.get(asset, 0.0)

    return {
        "planned_risk_reward": float(np.clip(planned_rr, 0.1, 10.0)),
        "emotional_bias_score": float(bias_score),
        "is_long": float(is_long),
        "hour_of_day": float(hour),
        "day_of_week": float(day),
        "rolling_win_rate": float(np.clip(rolling_wr, 0.0, 1.0)),
        "consecutive_losses": float(consecutive_losses),
        "asset_class_code": float(asset_code),
    }


def to_feature_dataframe(feature_dict: Dict[str, float]) -> pd.DataFrame:
    """Format single feature dict into DataFrame with matching column names for inference."""
    row = [feature_dict[col] for col in FEATURE_COLUMNS]
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)
