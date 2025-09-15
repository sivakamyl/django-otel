import logging
from opentelemetry import trace as otel_trace  # Rename to avoid conflict

# Define TRACE level constant
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")

# Add trace method to Logger class
def trace_method(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)

logging.Logger.trace = trace_method

class ContextLogger:
    """
    Singleton logger fully abstracted for Django apps.
    Handles:
      - TRACE, INFO, WARNING, ERROR, CRITICAL, EXCEPTION
      - Custom events / page views
      - Automatically sends to Azure App Insights
    """
    def __init__(self, logger_name="django_otel"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        # Add console handler for local dev
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
            self.logger.addHandler(console_handler)

    # Standard log levels
    def trace(self, message, **context):
        self.logger.trace(message, extra={"custom_dimensions": context})

    def debug(self, message, **context):
        self.logger.debug(message, extra={"custom_dimensions": context})

    def info(self, message, **context):
        self.logger.info(message, extra={"custom_dimensions": context})

    def warning(self, message, **context):
        self.logger.warning(message, extra={"custom_dimensions": context})

    def error(self, message, **context):
        self.logger.error(message, extra={"custom_dimensions": context})

    def critical(self, message, **context):
        self.logger.critical(message, extra={"custom_dimensions": context})

    def exception(self, message, **context):
        self.logger.exception(message, extra={"custom_dimensions": context})

    # Custom event / page view
    def custom_event(self, name, properties=None, severity="INFO"):
        """
        Log a custom event.
        :param name: Event name, e.g., 'page_view'
        :param properties: Dict of extra metadata
        :param severity: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        properties = properties or {}
        
        # Get the current span context for correlation (with error handling)
        trace_id = None
        try:
            current_span = otel_trace.get_current_span()  # Use renamed import
            if current_span and hasattr(current_span, 'get_span_context'):
                span_context = current_span.get_span_context()
                if span_context and hasattr(span_context, 'trace_id'):
                    trace_id = span_context.trace_id
        except Exception as e:
            # Silently fail if tracing is not available
            pass
        
        # Create log record with custom dimensions
        custom_dims = {
            'event_name': name,
            **properties
        }
        
        # Add trace context if available
        if trace_id:
            custom_dims['trace_id'] = f"{trace_id:032x}"
    
        SEVERITY_MAP = {
            "TRACE": TRACE_LEVEL,
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        level = SEVERITY_MAP.get(severity.upper(), logging.INFO)
        
        self.logger.log(level, f"CustomEvent: {name}", extra={"custom_dimensions": custom_dims})
    
    def page_view(self, name="page_view", properties=None):
        """Convenience method for page views"""
        properties = properties or {}
        self.custom_event(name, properties, severity="INFO")

    # Additional convenience methods
    def track_user_action(self, action_name, user_id=None, **properties):
        """Track user actions with user context"""
        props = {
            'action_type': 'user_action',
            'action_name': action_name,
            **properties
        }
        if user_id:
            props['user_id'] = str(user_id)
        self.custom_event(f"user_action_{action_name}", props, severity="INFO")

    def track_api_call(self, endpoint, method, status_code, **properties):
        """Track API calls"""
        props = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            **properties
        }
        self.custom_event("api_call", props, severity="INFO")

# singleton instance
contextLogger = ContextLogger()