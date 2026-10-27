from django.urls import path
from ml.views import PreTradePredictionView

app_name = "ml"

urlpatterns = [
    path("predict/", PreTradePredictionView.as_view(), name="predict"),
]
