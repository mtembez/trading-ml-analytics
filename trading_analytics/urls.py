from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/trades/", include("apps.trades.urls", namespace="trades")),
    path("api/v1/analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("api/v1/ml/", include("ml.urls", namespace="ml")),
]
