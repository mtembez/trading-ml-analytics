"""Production inference engine for behavioral trade outcome prediction and risk guardrails."""

import logging
from pathlib import Path
from typing import Any, Dict
import joblib
from django.conf import settings
from ml.features import extract_trade_features, to_feature_dataframe

logger = logging.getLogger(__name__)


class TradeOutcomePredictor:
    """Production ML inference engine scoring trade success probability and behavioral risk."""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model_path = getattr(
            settings,
            "ML_MODEL_PATH",
            Path(__file__).resolve().parent / "models" / "trade_outcome_rf.joblib",
        )
        self.model = self._load_model()

    def _load_model(self):
        path = Path(self.model_path)
        if path.exists():
            try:
                model = joblib.load(path)
                logger.info("Loaded trade outcome model from %s", path)
                return model
            except Exception as exc:
                logger.warning("Failed to load model from %s: %s", path, exc)
        return None

    def predict_trade_risk(self, trade_input: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate pre-trade submission, returning win probability and psychological guardrails."""
        features = extract_trade_features(trade_input)
        df_features = to_feature_dataframe(features)

        win_prob = 0.50
        if self.model is not None:
            try:
                probs = self.model.predict_proba(df_features)[0]
                win_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            except Exception as exc:
                logger.warning("ML inference failed, using heuristic: %s", exc)
                win_prob = self._heuristic_prob(features)
        else:
            win_prob = self._heuristic_prob(features)

        win_prob = max(0.05, min(0.95, win_prob))

        # Behavioral heuristics and guardrail triggers
        warnings = []
        emotion = str(trade_input.get("emotional_state", "disciplined")).lower()
        rr = features["planned_risk_reward"]
        consecutive_losses = features["consecutive_losses"]

        if emotion in ["revenge"]:
            warnings.append("CRITICAL: Revenge trading detected following previous losses. High probability of tilt.")
        elif emotion in ["fomo"]:
            warnings.append("WARNING: FOMO entry detected. Setup may be chased with poor entry price.")
        elif emotion in ["greedy"]:
            warnings.append("WARNING: Greed bias detected. Verify stop loss adherence and position sizing.")

        if rr < 1.0:
            warnings.append(f"UNFAVORABLE ASYMMETRY: Planned Risk/Reward ({rr:.2f}) is below 1.0 minimum threshold.")

        if consecutive_losses >= 3:
            warnings.append(f"STRESS ALERT: {int(consecutive_losses)} consecutive losses recorded. Risk per trade should be halved.")

        # Determine Risk Level
        if emotion in ["revenge"] or (consecutive_losses >= 3 and emotion in ["fomo", "greedy"]):
            risk_level = "CRITICAL_GUARDRAIL"
            recommendation = "REJECT TRADE: Active tilt risk. Step away from terminal for mandatory 30-minute cooldown."
        elif win_prob < 0.40 or len(warnings) >= 2:
            risk_level = "HIGH"
            recommendation = "EXERCISE CAUTION: Multiple behavioral headwinds identified. Reduce position size by 50%."
        elif win_prob < 0.52:
            risk_level = "MODERATE"
            recommendation = "ACCEPTABLE: Verify strict adherence to stop loss and avoid early profit-taking."
        else:
            risk_level = "LOW"
            recommendation = "FAVORABLE SETUP: High discipline score and positive statistical expectation."

        return {
            "win_probability": round(win_prob, 3),
            "expected_outcome": "WIN" if win_prob >= 0.50 else "LOSS",
            "risk_level": risk_level,
            "recommendation": recommendation,
            "behavioral_warnings": warnings,
            "extracted_features": features,
        }

    def _heuristic_prob(self, features: dict) -> float:
        """Deterministic baseline probability calculation if model file is not present."""
        bias = features["emotional_bias_score"]
        rr = features["planned_risk_reward"]
        p = 0.55 - (bias * 0.12) + ((rr - 1.5) * 0.05)
        return float(max(0.10, min(0.90, p)))
