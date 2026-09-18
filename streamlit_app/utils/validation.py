"""Data validation and sanity verification utilities for CustomerAtlas.

Ensures analytical integrity, validates dataset schemas, checks for missing
or corrupted records, and prevents silent calculation errors.
"""

from typing import List, Optional, Tuple
import pandas as pd
import streamlit as st


REQUIRED_CUSTOMER_COLUMNS = [
    "customer_id",
    "total_spend",
    "total_orders",
    "avg_order_value",
    "recency_days",
    "frequency",
    "monetary",
    "rfm_segment",
    "churn_probability",
    "predicted_clv",
]


def validate_customer_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate customer feature dataset against required enterprise schema.

    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    if df is None or df.empty:
        return False, ["Customer dataset is empty or uninitialized."]

    missing_cols = [col for col in REQUIRED_CUSTOMER_COLUMNS if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {', '.join(missing_cols)}")

    if "customer_id" in df.columns and df["customer_id"].isnull().any():
        null_count = int(df["customer_id"].isnull().sum())
        issues.append(f"Dataset contains {null_count:,} null customer IDs.")

    if "total_spend" in df.columns and (df["total_spend"] < 0).any():
        neg_count = int((df["total_spend"] < 0).sum())
        issues.append(f"Dataset contains {neg_count:,} negative spend records.")

    if "churn_probability" in df.columns:
        invalid_churn = ((df["churn_probability"] < 0) | (df["churn_probability"] > 1)).sum()
        if invalid_churn > 0:
            issues.append(f"Dataset contains {invalid_churn:,} invalid churn probabilities out of [0, 1].")

    is_valid = len(issues) == 0
    return is_valid, issues


def validate_customer_id(customer_id: Optional[str], df: pd.DataFrame) -> bool:
    """Check whether a customer ID exists in the canonical feature dataset."""
    if not customer_id or df is None or df.empty:
        return False
    return str(customer_id) in set(df["customer_id"].astype(str))
