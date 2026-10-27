from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ml.predictor import TradeOutcomePredictor


class PreTradePredictionView(APIView):
    """Pre-trade risk assessment and machine learning win probability prediction."""

    def post(self, request):
        trade_data = request.data
        if not isinstance(trade_data, dict):
            return Response({"error": "Request body must be a JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        predictor = TradeOutcomePredictor.get_instance()
        result = predictor.predict_trade_risk(trade_data)
        return Response(result, status=status.HTTP_200_OK)
