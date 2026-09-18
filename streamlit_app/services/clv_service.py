"""Customer Lifetime Value (CLV) Intelligence Service for CustomerAtlas.

Provides portfolio CLV summary metrics, dynamic value distribution binning,
CLV segment/regional breakdowns, and high-value customer analysis.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from utils.formatting import format_brl, format_pct


def compute_clv_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate forward 12-month customer lifetime value benchmarks."""
    if df is None or df.empty or "predicted_clv" not in df.columns:
        return {
            "avg_clv": 0.0,
            "median_clv": 0.0,
            "p90_clv": 0.0,
            "p95_clv": 0.0,
            "total_pipeline_clv": 0.0,
            "top_10_pct_avg": 0.0,
            "total_customers": 0,
        }

    clv_series = df["predicted_clv"].dropna()
    p90 = float(clv_series.quantile(0.90))
    p95 = float(clv_series.quantile(0.95))
    top_10_avg = float(clv_series[clv_series >= p90].mean()) if not clv_series.empty else 0.0

    return {
        "avg_clv": float(clv_series.mean()),
        "median_clv": float(clv_series.median()),
        "p90_clv": p90,
        "p95_clv": p95,
        "total_pipeline_clv": float(clv_series.sum()),
        "top_10_pct_avg": top_10_avg,
        "total_customers": len(df),
    }


def compute_clv_bins(df: pd.DataFrame) -> pd.DataFrame:
    """Group customers into standardized, dynamic CLV value brackets."""
    if df is None or df.empty or "predicted_clv" not in df.columns:
        return pd.DataFrame()

    clv_vals = df["predicted_clv"].fillna(0)
    bins = [-np.inf, 100, 250, 500, 1000, np.inf]
    labels = ["< R$100", "R$100 – R$250", "R$250 – R$500", "R$500 – R$1,000", "> R$1,000"]

    df_binned = df.copy()
    df_binned["clv_bracket"] = pd.cut(clv_vals, bins=bins, labels=labels, right=False)

    summary = (
        df_binned.groupby("clv_bracket", observed=False)
        .agg(
            customers=("customer_id", "count"),
            total_historical_spend=("total_spend", "sum"),
            total_predicted_clv=("predicted_clv", "sum"),
            avg_churn_prob=("churn_probability", "mean"),
        )
        .reset_index()
    )

    total_c = len(df)
    total_rev = df["total_spend"].sum()
    summary["customer_pct"] = summary["customers"] / max(1, total_c)
    summary["revenue_pct"] = summary["total_historical_spend"] / max(1, total_rev)

    return summary


def analyze_high_value_cohort(df: pd.DataFrame, percentile: float = 0.90) -> Dict[str, Any]:
    """Perform explicit analytical breakdown of the Top High-Value Customer Cohort."""
    if df is None or df.empty or "predicted_clv" not in df.columns:
        return {
            "threshold": 0.0,
            "cohort_df": pd.DataFrame(),
            "count": 0,
            "pct_of_base": 0.0,
            "revenue_contribution": 0.0,
            "revenue_share": 0.0,
            "avg_clv": 0.0,
            "avg_frequency": 0.0,
            "avg_recency": 0.0,
            "risk_distribution": {},
        }

    threshold = float(df["predicted_clv"].quantile(percentile))
    high_val = df[df["predicted_clv"] >= threshold].copy()

    total_base = len(df)
    total_spend = df["total_spend"].sum()
    h_spend = high_val["total_spend"].sum()

    # Risk breakdown inside high-value cohort
    risk_counts = {}
    if "churn_probability" in high_val.columns:
        risk_counts["Low Risk (<35%)"] = int((high_val["churn_probability"] < 0.35).sum())
        risk_counts["Medium Risk (35-65%)"] = int(((high_val["churn_probability"] >= 0.35) & (high_val["churn_probability"] < 0.65)).sum())
        risk_counts["High Risk (>=65%)"] = int((high_val["churn_probability"] >= 0.65).sum())

    return {
        "threshold": threshold,
        "cohort_df": high_val.sort_values("predicted_clv", ascending=False),
        "count": len(high_val),
        "pct_of_base": len(high_val) / max(1, total_base),
        "revenue_contribution": h_spend,
        "revenue_share": h_spend / max(1, total_spend),
        "avg_clv": float(high_val["predicted_clv"].mean()),
        "avg_frequency": float(high_val["total_orders"].mean()),
        "avg_recency": float(high_val["recency_days"].mean()),
        "risk_distribution": risk_counts,
    }
