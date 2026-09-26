"""Structured application logging configuration for CustomerAtlas.

Provides a unified logger across presentation, service, API, and data layers with
standardized formatting and configurable log levels.
"""

import sys
from pathlib import Path

# Ensure streamlit_app is accessible in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "streamlit_app"
for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Re-export from canonical logging module
from streamlit_app.utils.logging_config import setup_logger, logger

__all__ = ["setup_logger", "logger"]
