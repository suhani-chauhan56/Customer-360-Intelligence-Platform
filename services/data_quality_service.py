"""Data Quality & System Health Service for CustomerAtlas.

Provides automated data validation audits, completeness checks, numeric range
diagnostics, and factual system health status reporting.
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from utils.validation import REQUIRED_CUSTOMER_COLUMNS


def run_data_quality_audit(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform a comprehensive data quality check on customer feature store."""
    if df is None or df.empty:
        return {
            "is_healthy": False,
            "quality_score_pct": 0.0,
            "total_records": 0,
            "total_columns": 0,
            "duplicate_customer_ids": 0,
            "null_customer_ids": 0,
            "negative_spend_records": 0,
            "invalid_churn_probabilities": 0,
            "missing_required_columns": REQUIRED_CUSTOMER_COLUMNS,
            "checks": [],
        }

    total_rows = len(df)
    total_cols = len(df.columns)

    # 1. Check required columns
    missing_required = [c for c in REQUIRED_CUSTOMER_COLUMNS if c not in df.columns]
    check_cols_pass = len(missing_required) == 0

    # 2. Check duplicate customer IDs
    dup_ids = int(df["customer_id"].duplicated().sum()) if "customer_id" in df.columns else 0
    check_dup_pass = dup_ids == 0

    # 3. Check null customer IDs
    null_ids = int(df["customer_id"].isnull().sum()) if "customer_id" in df.columns else 0
    check_null_pass = null_ids == 0

    # 4. Check negative spend records
    neg_spend = int((df["total_spend"] < 0).sum()) if "total_spend" in df.columns else 0
    check_spend_pass = neg_spend == 0

    # 5. Check churn probability range [0.0, 1.0]
    if "churn_probability" in df.columns:
        invalid_churn = int(((df["churn_probability"] < 0.0) | (df["churn_probability"] > 1.0)).sum())
    else:
        invalid_churn = 0
    check_churn_pass = invalid_churn == 0

    # 6. Check order count sanity (orders >= 1)
    if "total_orders" in df.columns:
        invalid_orders = int((df["total_orders"] < 1).sum())
    else:
        invalid_orders = 0
    check_orders_pass = invalid_orders == 0

    checks = [
        {"Test": "Required Schema Columns", "Status": "Passed 🟢" if check_cols_pass else "Failed 🔴", "Detail": f"{len(REQUIRED_CUSTOMER_COLUMNS) - len(missing_required)}/{len(REQUIRED_CUSTOMER_COLUMNS)} required columns present"},
        {"Test": "Customer ID Uniqueness", "Status": "Passed 🟢" if check_dup_pass else "Failed 🔴", "Detail": f"{dup_ids:,} duplicate customer ID records"},
        {"Test": "Customer ID Completeness", "Status": "Passed 🟢" if check_null_pass else "Failed 🔴", "Detail": f"{null_ids:,} missing/null ID records"},
        {"Test": "Non-Negative Revenue", "Status": "Passed 🟢" if check_spend_pass else "Failed 🔴", "Detail": f"{neg_spend:,} negative spend anomalies"},
        {"Test": "Calibrated Churn Range", "Status": "Passed 🟢" if check_churn_pass else "Failed 🔴", "Detail": f"{invalid_churn:,} out-of-range probabilities"},
        {"Test": "Order Count Sanity", "Status": "Passed 🟢" if check_orders_pass else "Failed 🔴", "Detail": f"{invalid_orders:,} non-positive order records"},
    ]

    passed_count = sum(1 for c in [check_cols_pass, check_dup_pass, check_null_pass, check_spend_pass, check_churn_pass, check_orders_pass] if c)
    quality_score = (passed_count / 6.0) * 100.0

    return {
        "is_healthy": quality_score >= 99.0,
        "quality_score_pct": round(quality_score, 1),
        "total_records": total_rows,
        "total_columns": total_cols,
        "duplicate_customer_ids": dup_ids,
        "null_customer_ids": null_ids,
        "negative_spend_records": neg_spend,
        "invalid_churn_probabilities": invalid_churn,
        "missing_required_columns": missing_required,
        "checks": checks,
    }
