# public package API
default_app_config = "django_otel.apps.DjangoOtelConfig"
__all__ = ["configure_opentelemetry"]

from .logger import contextLogger
from .config import configure_opentelemetry
