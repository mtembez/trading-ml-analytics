import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ml.features import extract_trade_features, to_feature_dataframe
from ml.predictor import TradeOutcomePredictor
from ml.train_predictor import train_and_export_model


@pytest.fixture
def api_client():
    return APIClient()


class TestMLBehavioralPrediction:
    def test_feature_extraction_pipeline(self):
        trade_input = {
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "emotional_state": "disciplined",
            "position_type": "LONG",
            "hour_of_day": 14,
            "day_of_week": 2,
            "rolling_win_rate": 0.65,
            "consecutive_losses": 0,
            "asset_class": "forex",
        }
        feats = extract_trade_features(trade_input)
        assert feats["planned_risk_reward"] == 2.0  # (110 - 100) / (100 - 95) = 10 / 5 = 2.0
        assert feats["emotional_bias_score"] == 0.0  # Disciplined
        assert feats["is_long"] == 1.0

        df = to_feature_dataframe(feats)
        assert df.shape == (1, 8)
        assert list(df.columns) == [
            "planned_risk_reward",
            "emotional_bias_score",
            "is_long",
            "hour_of_day",
            "day_of_week",
            "rolling_win_rate",
            "consecutive_losses",
            "asset_class_code",
        ]

    def test_predictor_guardrail_disciplined_trade(self):
        predictor = TradeOutcomePredictor.get_instance()
        trade_input = {
            "entry_price": 1.2000,
            "stop_loss": 1.1950,
            "take_profit": 1.2150,  # 3:1 RR
            "emotional_state": "disciplined",
            "position_type": "LONG",
            "hour_of_day": 10,
            "rolling_win_rate": 0.60,
            "consecutive_losses": 0,
        }
        res = predictor.predict_trade_risk(trade_input)
        assert "win_probability" in res
        assert 0.0 < res["win_probability"] < 1.0
        assert res["risk_level"] in ["LOW", "MODERATE"]
        assert len(res["behavioral_warnings"]) == 0

    def test_predictor_guardrail_revenge_trading_triggers_rejection(self):
        predictor = TradeOutcomePredictor.get_instance()
        trade_input = {
            "entry_price": 100.0,
            "stop_loss": 99.0,
            "take_profit": 100.5,  # 0.5 RR
            "emotional_state": "revenge",
            "position_type": "LONG",
            "consecutive_losses": 3,
        }
        res = predictor.predict_trade_risk(trade_input)
        assert res["risk_level"] == "CRITICAL_GUARDRAIL"
        assert "REJECT TRADE" in res["recommendation"]
        assert any("Revenge trading detected" in w for w in res["behavioral_warnings"])

    def test_ml_predict_rest_api_endpoint(self, api_client):
        url = reverse("ml:predict")
        payload = {
            "entry_price": 50000.0,
            "stop_loss": 49000.0,
            "take_profit": 53000.0,
            "emotional_state": "disciplined",
            "position_type": "LONG",
            "asset_class": "crypto",
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert "win_probability" in data
        assert "risk_level" in data
        assert "recommendation" in data

    def test_train_and_export_model_pipeline(self, tmp_path):
        model_file = tmp_path / "test_model.joblib"
        metrics = train_and_export_model(output_path=model_file)
        assert metrics["accuracy"] > 0.50
        assert model_file.exists()
