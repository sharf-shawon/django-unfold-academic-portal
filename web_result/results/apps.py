from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResultsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web_result.results"
    verbose_name = _("Academic Results")
