import logging

def contextLogger(logger: logging.Logger, level: str, message: str, **context):
    """
    Log a message with contextual fields (extra data for Azure App Insights).
    Example:
        log_with_context(logger, "warning", "Minor issue", user_id=42)
    """
    # Map string to logger method
    level = level.lower()
    extra = {"custom_dimensions": context}

    if level == "trace":  # If using custom TRACE level
        logger.log(5, message, extra=extra)
    elif level == "debug":
        logger.debug(message, extra=extra)
    elif level == "info":
        logger.info(message, extra=extra)
    elif level == "warning":
        logger.warning(message, extra=extra)
    elif level == "error":
        logger.error(message, extra=extra)
    elif level == "critical":
        logger.critical(message, extra=extra)
    elif level == "exception":
        logger.exception(message, extra=extra)
    else:
        logger.info(message, extra=extra)
