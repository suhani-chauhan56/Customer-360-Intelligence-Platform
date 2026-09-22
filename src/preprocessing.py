"""Preprocessing and feature engineering utilities for CustomerAtlas."""

from typing import List, Optional
import numpy as np
import pandas as pd


def clean_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Sanitize and clean raw/processed customer feature frame."""
    if df is None or df.empty:
        return pd.DataFrame()

    clean_df = df.copy()

    # Deduplicate by customer_id if present
    if "customer_id" in clean_df.columns:
        clean_df = clean_df.drop_duplicates(subset=["customer_id"])

    # Ensure non-negative financial and count fields
    numeric_cols = ["total_spend", "avg_order_value", "total_orders", "recency_days", "frequency", "monetary"]
    for col in numeric_cols:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce").fillna(0.0)
            clean_df[col] = clean_df[col].clip(lower=0.0)

    # Churn probability clipping
    if "churn_probability" in clean_df.columns:
        clean_df["churn_probability"] = pd.to_numeric(clean_df["churn_probability"], errors="coerce").fillna(0.5)
        clean_df["churn_probability"] = clean_df["churn_probability"].clip(lower=0.0, upper=1.0)

    return clean_df


def derive_rfm_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate quintile R, F, M scores from numeric attributes."""
    if df is None or df.empty:
        return pd.DataFrame()

    res = df.copy()
    if "recency_days" in res.columns:
        # Lower recency -> higher score
        res["r_score"] = pd.qcut(res["recency_days"].rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)

    if "frequency" in res.columns:
        res["f_score"] = pd.qcut(res["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    if "monetary" in res.columns:
        res["m_score"] = pd.qcut(res["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    if all(c in res.columns for c in ["r_score", "f_score", "m_score"]):
        res["rfm_score"] = res["r_score"] * 100 + res["f_score"] * 10 + res["m_score"]

    return res
