import os
import logging
from typing import Optional, Dict

def _safe_import(name: str):
    try:
        components = __import__(name, fromlist=['*'])
        return components
    except Exception:
        return None

def configure_otel(cfg: Optional[Dict] = None):
    """
    cfg (dict) recommended keys:
      - connection_string: (str) ApplicationInsights connection string
      - service_name: (str) service name to set in resource
      - enable_live_metrics: (bool)
      - logging_formatter: optional python logging.Formatter instance or format string
    """
    cfg = cfg or {}
    conn_str = cfg.get("connection_string") or os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    service_name = cfg.get("service_name", os.environ.get("OTEL_SERVICE_NAME", "django"))
    enable_live_metrics = cfg.get("enable_live_metrics", False)

    # 1) prefer azure-monitor-opentelemetry convenience method if available
    azure_distro = _safe_import("azure.monitor.opentelemetry")
    if azure_distro and hasattr(azure_distro, "configure_azure_monitor"):
        try:
            # takes priority; will configure traces/logs/metrics for you
            azure_distro.configure_azure_monitor(
                connection_string=conn_str,
                enable_live_metrics=enable_live_metrics,
                logging_formatter=cfg.get("logging_formatter"),
                logger_name=cfg.get("logger_name"),
            )
            logging.getLogger(__name__).info("Configured Azure Monitor OpenTelemetry distro")
            return
        except Exception as e:
            logging.getLogger(__name__).warning("azure.monitor.opentelemetry.configure_azure_monitor() failed: %s", e)

    # 2) fallback: build providers and exporters manually
    # imports (from opentelemetry SDK + azure exporter)
    otel_api = _safe_import("opentelemetry")
    sdk_trace = _safe_import("opentelemetry.sdk.trace")
    sdk_logs = _safe_import("opentelemetry.sdk._logs")
    trace_exporter_module = _safe_import("azure.monitor.opentelemetry.exporter")
    if not (sdk_trace and trace_exporter_module):
        logging.getLogger(__name__).warning("Required opentelemetry SDK or azure exporter not installed; skipping fine-grained setup.")
        return

    # RESOURCE
    try:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.resources import SERVICE_NAME
    except Exception:
        Resource = None
        SERVICE_NAME = "service.name"

    resource = Resource.create({SERVICE_NAME: service_name}) if Resource else None

    # TRACING setup
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry import trace
    azure_trace_exporter = None
    try:
        AzureMonitorTraceExporter = trace_exporter_module.AzureMonitorTraceExporter
        azure_trace_exporter = AzureMonitorTraceExporter(connection_string=conn_str) if conn_str else AzureMonitorTraceExporter()
    except Exception:
        azure_trace_exporter = None

    tracer_provider = TracerProvider(resource=resource) if resource else TracerProvider()
    if azure_trace_exporter:
        span_processor = BatchSpanProcessor(azure_trace_exporter)
        tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # INSTRUMENT Django automatically if opentelemetry-instrumentation-django is present
    django_instrumentor = _safe_import("opentelemetry.instrumentation.django")
    try:
        if django_instrumentor and hasattr(django_instrumentor, "DjangoInstrumentor"):
            django_instrumentor.DjangoInstrumentor().instrument()
            logging.getLogger(__name__).info("Applied django instrumentation")
    except Exception as e:
        logging.getLogger(__name__).warning("Django instrumentor failed: %s", e)

    # LOGGING setup (experimental; logs pipeline in OTel still evolving)
    try:
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        AzureMonitorLogExporter = trace_exporter_module.AzureMonitorLogExporter
        logger_provider = LoggerProvider(resource=resource) if resource else LoggerProvider()
        set_logger_provider(logger_provider)
        log_exporter = AzureMonitorLogExporter(connection_string=conn_str) if conn_str else AzureMonitorLogExporter()
        lr_processor = BatchLogRecordProcessor(log_exporter)
        logger_provider.add_log_record_processor(lr_processor)

        # attach LoggingHandler to python logging
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        py_logger = logging.getLogger()
        py_logger.addHandler(handler)

        # optionally set formatter if provided
        fmt = cfg.get("logging_formatter")
        if isinstance(fmt, str):
            handler.setFormatter(logging.Formatter(fmt))
        elif fmt:
            handler.setFormatter(fmt)

        logging.getLogger(__name__).info("Configured OpenTelemetry logging -> Azure Monitor (experimental)")
    except Exception as e:
        logging.getLogger(__name__).warning("OTel logging config failed/unsupported: %s", e)

    # METRICS: left as an exercise (can add MeterProvider + AzureMonitorMetricExporter similarly)
