"""Centralized configuration and environment settings for CustomerAtlas.

Supports environment-driven configuration with sensible production defaults.
Avoids hardcoding machine-specific paths and keeps credentials secure.
"""

import os
from pathlib import Path
from typing import Dict, Any


# Resolve repository root directory safely relative to this file
CONFIG_DIR = Path(__file__).resolve().parent
APP_DIR = CONFIG_DIR.parent
ROOT_DIR = APP_DIR.parent

# Application Environment: 'development', 'testing', 'production'
APP_ENV: str = os.getenv("APP_ENV", "production").lower()

# Logging Configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# Data and Model Directory Paths (configurable via environment variables)
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(ROOT_DIR / "data" / "processed")))
RAW_DATA_DIR: Path = Path(os.getenv("RAW_DATA_DIR", str(ROOT_DIR / "data" / "raw")))
MODELS_DIR: Path = Path(os.getenv("MODELS_DIR", str(ROOT_DIR / "models")))
METADATA_DIR: Path = MODELS_DIR / "metadata"
SQL_DIR: Path = Path(os.getenv("SQL_DIR", str(ROOT_DIR / "sql")))
ASSETS_DIR: Path = APP_DIR / "assets"

# Application Metadata
APP_NAME: str = "CustomerAtlas"
APP_VERSION: str = "2.0.0-prod"
APP_RELEASE_DATE: str = "2026-09-18"
APP_DESCRIPTION: str = "Unified Customer Intelligence & Decision Support Platform"

# Caching & Performance Settings
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
MAX_SCATTER_SAMPLE_SIZE: int = int(os.getenv("MAX_SCATTER_SAMPLE_SIZE", "2500"))

# Currency and Localization
CURRENCY_CODE: str = "BRL"
CURRENCY_SYMBOL: str = "R$"


def get_environment_info() -> Dict[str, Any]:
    """Retrieve runtime environment diagnostics safely."""
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "environment": APP_ENV,
        "log_level": LOG_LEVEL,
        "data_dir_exists": DATA_DIR.exists(),
        "models_dir_exists": MODELS_DIR.exists(),
        "currency": f"{CURRENCY_SYMBOL} ({CURRENCY_CODE})",
    }
