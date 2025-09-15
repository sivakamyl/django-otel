from django.apps import AppConfig
from django.conf import settings
from .config import configure_opentelemetry

class DjangoOtelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_otel"

    def ready(self):
        conn_str = getattr(settings, "APPINSIGHTS_CONNECTION_STRING", None)
        if conn_str:
            configure_opentelemetry(conn_str)
