"""Compatibility re-export of canonical validation utilities from utils.validation."""

from utils.validation import (
    REQUIRED_CUSTOMER_COLUMNS,
    validate_customer_dataframe,
    validate_customer_id,
)

__all__ = [
    "REQUIRED_CUSTOMER_COLUMNS",
    "validate_customer_dataframe",
    "validate_customer_id",
]
