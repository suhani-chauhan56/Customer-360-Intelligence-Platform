"""Configuration package for CustomerAtlas."""

from config.settings import (
    APP_NAME,
    APP_VERSION,
    APP_ENV,
    DATA_DIR,
    RAW_DATA_DIR,
    MODELS_DIR,
    METADATA_DIR,
    SQL_DIR,
    ASSETS_DIR,
    LOG_LEVEL,
    CACHE_TTL_SECONDS,
    CURRENCY_CODE,
    CURRENCY_SYMBOL,
    get_environment_info,
)
from config.thresholds import (
    CHURN_THRESHOLD_LOW_MAX,
    CHURN_THRESHOLD_HIGH_MIN,
    RECENCY_DAYS_RECENT,
    RECENCY_DAYS_ACTIVE,
    RECENCY_DAYS_LAPSED,
    CLV_P90_PERCENTILE,
)
from config.business_rules import (
    SEGMENT_RULES,
    CLV_BAND_LABELS,
    get_retention_playbook,
)

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "APP_ENV",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "MODELS_DIR",
    "METADATA_DIR",
    "SQL_DIR",
    "ASSETS_DIR",
    "LOG_LEVEL",
    "CACHE_TTL_SECONDS",
    "CURRENCY_CODE",
    "CURRENCY_SYMBOL",
    "get_environment_info",
    "CHURN_THRESHOLD_LOW_MAX",
    "CHURN_THRESHOLD_HIGH_MIN",
    "RECENCY_DAYS_RECENT",
    "RECENCY_DAYS_ACTIVE",
    "RECENCY_DAYS_LAPSED",
    "CLV_P90_PERCENTILE",
    "SEGMENT_RULES",
    "CLV_BAND_LABELS",
    "get_retention_playbook",
]
