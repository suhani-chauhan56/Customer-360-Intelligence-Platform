"""Structured application logging configuration for CustomerAtlas.

Provides a unified logger across presentation, service, and data layers with
standardized formatting and configurable log levels.
"""

import logging
import sys
from typing import Optional
from config.settings import LOG_LEVEL


_LOGGERS = {}


def setup_logger(name: str = "customer_atlas", level: Optional[str] = None) -> logging.Logger:
    """Create or retrieve a standardized application logger."""
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    log_level = level or LOG_LEVEL

    try:
        logger.setLevel(getattr(logging, log_level))
    except (AttributeError, TypeError):
        logger.setLevel(logging.INFO)

    # Avoid adding multiple duplicate handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    _LOGGERS[name] = logger
    return logger


# Default application logger instance
logger = setup_logger()
