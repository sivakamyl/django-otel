# django-otel

Seamlessly integrate OpenTelemetry and Azure Application Insights with Django.
This package provides:
✅ Automatic instrumentation for Django apps.
✅ Reload-safe initialization (prevents multiple OTEL setups in Django’s development mode).
✅ Standard logs (TRACE → CRITICAL) sent to Application Insights.
✅ Console logging preserved for local debugging.


## Installation

```bash
pip install django-otel


** ⚙️ Configuration in settings.py **

Add the following to your Django settings.py:

INSTALLED_APPS += ["django_otel"]

# Azure Application Insights Connection String
APPINSIGHTS_CONNECTION_STRING = "InstrumentationKey=YOUR-INSTRUMENTATION-KEY"
SERVICE_NAME = "YOUR-SERVICE-NAME"

from django_otel.config import configure_opentelemetry
configure_opentelemetry(
    connection_string=APPINSIGHTS_CONNECTION_STRING,
    service_name=SERVICE_NAME
)


This ensures OTEL is configured before Django finishes loading.


** 🧰 Usage **

from django_otel import contextLogger

contextLogger.trace("Entering view", path=request.path)
contextLogger.info("Page accessed", path=request.path)
contextLogger.debug("Page debug", path=request.path)
contextLogger.critical("Critical", path=request.path)
contextLogger.warning("Page warning", path=request.path)

These logs will appear in AZURE Application Insights Logs → Traces (TRACE → CRITICAL)


✅ Custom Events support (including page views as events). - WIP