import os
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Module-level flag to prevent multiple initializations
_otel_initialized = False

def configure_opentelemetry(connection_string: str = None, service_name: str = "django-app"):
    """
    Initialize OpenTelemetry with Azure Application Insights.
    This function is reload-safe in Django development mode.
    """
    global _otel_initialized
    if _otel_initialized:
        return trace.get_tracer(__name__)

    connection_string = connection_string or os.getenv("APPINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("Azure Application Insights connection string is required.")

    # Auto configure Azure Monitor
    configure_azure_monitor(connection_string=connection_string)

    # Tracer provider
    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Exporter
    exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(span_processor)

    _otel_initialized = True
    return trace.get_tracer(__name__)
