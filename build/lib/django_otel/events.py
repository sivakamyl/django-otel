import logging

# Logger for custom events
logger = logging.getLogger("django_otel.events")

def custom_event(name: str, properties: dict = None, severity: str = "INFO"):
    """
    Send a custom event to Azure Application Insights via logging pipeline.
    
    :param name: Name of the event (e.g., "page_view", "user_signup").
    :param properties: Dictionary of custom dimensions (extra metadata).
    :param severity: Log severity: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    properties = properties or {}

    # Map severity string to logging level
    level = getattr(logging, severity.upper(), logging.INFO)

    # Include properties as custom_dimensions (Application Insights standard)
    logger.log(level, f"CustomEvent: {name}", extra={"custom_dimensions": properties})
