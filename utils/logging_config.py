"""Canonical structured application logging configuration for CustomerAtlas.

Provides a unified logger across presentation, service, API, and data layers with
standardized formatting and configurable log levels. Self-contained with zero circular dependencies.
"""

import logging
import os
import sys
from typing import Dict, Optional

_LOGGERS: Dict[str, logging.Logger] = {}


def setup_logger(name: str = "customer_atlas", level: Optional[str] = None) -> logging.Logger:
    """Create or retrieve a standardized application logger."""
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger_inst = logging.getLogger(name)
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()

    try:
        logger_inst.setLevel(getattr(logging, log_level))
    except (AttributeError, TypeError):
        logger_inst.setLevel(logging.INFO)

    # Avoid adding multiple duplicate handlers if already configured
    if not logger_inst.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger_inst.addHandler(handler)

    logger_inst.propagate = False
    _LOGGERS[name] = logger_inst
    return logger_inst


# Default application logger instance
logger = setup_logger()

__all__ = ["setup_logger", "logger"]
