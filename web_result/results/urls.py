from django.urls import path

from .views import HealthCheckView
from .views import ResultPublicView

app_name = "results"

urlpatterns = [
    path("", ResultPublicView.as_view(), name="public_index"),
    path("healthz/", HealthCheckView.as_view(), name="healthz"),
]
