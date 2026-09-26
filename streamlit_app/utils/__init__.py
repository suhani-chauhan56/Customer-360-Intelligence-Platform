"""Compatibility re-exports for streamlit_app.utils -> canonical utils package."""

from utils.formatting import (
    format_number,
    format_currency,
    format_percent,
    format_brl,
    format_pct,
    format_num,
)
from utils.styling import (
    load_css,
    style_chart,
    chart,
    CHART_COLORWAY,
    COLOR_PRIMARY,
    COLOR_CYAN,
    COLOR_PURPLE,
    COLOR_AMBER,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_SLATE,
    PLOT_CONFIG,
)
from utils.validation import (
    validate_customer_dataframe,
    validate_customer_id,
    REQUIRED_CUSTOMER_COLUMNS,
)
from utils.logging_config import logger, setup_logger
from utils.exceptions import (
    CustomerAtlasError,
    DataValidationError,
    DataLoadError,
    ModelLoadError,
    ModelInferenceError,
    ConfigurationError,
)
from utils.helpers import safe_float, safe_int, safe_str, calculate_pareto_cutoff, calculate_data_snapshot_info

__all__ = [
    "format_number",
    "format_currency",
    "format_percent",
    "format_brl",
    "format_pct",
    "format_num",
    "load_css",
    "style_chart",
    "chart",
    "CHART_COLORWAY",
    "COLOR_PRIMARY",
    "COLOR_CYAN",
    "COLOR_PURPLE",
    "COLOR_AMBER",
    "COLOR_RED",
    "COLOR_GREEN",
    "COLOR_SLATE",
    "PLOT_CONFIG",
    "validate_customer_dataframe",
    "validate_customer_id",
    "REQUIRED_CUSTOMER_COLUMNS",
    "logger",
    "setup_logger",
    "CustomerAtlasError",
    "DataValidationError",
    "DataLoadError",
    "ModelLoadError",
    "ModelInferenceError",
    "ConfigurationError",
    "safe_float",
    "safe_int",
    "safe_str",
    "calculate_pareto_cutoff",
    "calculate_data_snapshot_info",
]
