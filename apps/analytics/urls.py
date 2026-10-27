from django.urls import path
from apps.analytics.views import (
    BehavioralAnalyticsView,
    EquityCurveView,
    OverviewAnalyticsView,
)

app_name = "analytics"

urlpatterns = [
    path("overview/", OverviewAnalyticsView.as_view(), name="overview"),
    path("equity-curve/", EquityCurveView.as_view(), name="equity-curve"),
    path("behavioral/", BehavioralAnalyticsView.as_view(), name="behavioral"),
]
