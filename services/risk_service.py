"""Customer Risk and Churn Intelligence Service for CustomerAtlas.

Provides at-risk revenue exposure calculation, risk distribution analytics,
high-value vs high-risk matrix modeling, and transparent customer prioritization.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from utils.formatting import format_brl, format_pct


def compute_risk_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute customer risk benchmarks and total revenue at risk."""
    if df is None or df.empty or "churn_probability" not in df.columns:
        return {
            "total_customers": 0,
            "at_risk_count": 0,
            "at_risk_pct": 0.0,
            "at_risk_revenue": 0.0,
            "at_risk_rev_pct": 0.0,
            "high_val_at_risk_count": 0,
            "high_val_at_risk_rev": 0.0,
            "avg_churn_prob": 0.0,
        }

    total_customers = len(df)
    total_rev = df["total_spend"].sum()

    # Define at-risk threshold at calibrated >= 0.65
    at_risk_df = df[df["churn_probability"] >= 0.65]
    at_risk_count = len(at_risk_df)
    at_risk_rev = at_risk_df["total_spend"].sum()

    # High-Value at risk (top 25% spenders or spend >= 200 within at-risk group)
    p75_spend = df["total_spend"].quantile(0.75)
    hv_at_risk = at_risk_df[at_risk_df["total_spend"] >= p75_spend]

    return {
        "total_customers": total_customers,
        "at_risk_count": at_risk_count,
        "at_risk_pct": at_risk_count / max(1, total_customers),
        "at_risk_revenue": at_risk_rev,
        "at_risk_rev_pct": at_risk_rev / max(1, total_rev),
        "high_val_at_risk_count": len(hv_at_risk),
        "high_val_at_risk_rev": hv_at_risk["total_spend"].sum(),
        "avg_churn_prob": float(df["churn_probability"].mean()),
    }


def compute_risk_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Classify customers into standard Low, Medium, and High risk tiers."""
    if df is None or df.empty or "churn_probability" not in df.columns:
        return pd.DataFrame()

    total_cust = len(df)
    total_spend = df["total_spend"].sum()

    df_risk = df.copy()
    bins = [-np.inf, 0.35, 0.65, np.inf]
    labels = ["Low Risk (<35%)", "Medium Risk (35-65%)", "High Risk (>=65%)"]
    df_risk["risk_tier"] = pd.cut(df_risk["churn_probability"], bins=bins, labels=labels)

    summary = (
        df_risk.groupby("risk_tier", observed=False)
        .agg(
            customers=("customer_id", "count"),
            total_revenue=("total_spend", "sum"),
            avg_clv=("predicted_clv", "mean"),
            avg_orders=("total_orders", "mean"),
            avg_recency=("recency_days", "mean"),
        )
        .reset_index()
    )

    summary["customer_share"] = summary["customers"] / max(1, total_cust)
    summary["revenue_share"] = summary["total_revenue"] / max(1, total_spend)

    return summary


def calculate_customer_prioritization(df: pd.DataFrame, top_n: int = 200) -> pd.DataFrame:
    """Derive transparent customer prioritization ranking.

    Formula:
        Priority Score = (Churn Probability) * (Normalized Predicted CLV) * 100
        where Normalized Predicted CLV = predicted_clv / 99th_percentile_clv (capped at 1.0)
    """
    if df is None or df.empty:
        return pd.DataFrame()

    p_df = df.copy()
    max_clv = p_df["predicted_clv"].quantile(0.99) if "predicted_clv" in p_df.columns else 1.0
    max_clv = max(1.0, max_clv)

    norm_clv = (p_df["predicted_clv"] / max_clv).clip(upper=1.0) if "predicted_clv" in p_df.columns else pd.Series(1.0, index=p_df.index)
    churn_p = p_df["churn_probability"] if "churn_probability" in p_df.columns else pd.Series(0.5, index=p_df.index)

    # Priority score ranges 0 - 100
    p_df["priority_score"] = (churn_p * norm_clv * 100.0).round(1)

    # Ensure canonical AOV is present and cleanly calculated
    if "avg_order_value" not in p_df.columns:
        if "total_spend" in p_df.columns and "total_orders" in p_df.columns:
            orders_safe = p_df["total_orders"].replace(0, np.nan)
            p_df["avg_order_value"] = (p_df["total_spend"] / orders_safe).fillna(0.0).round(2)
        elif "total_spend" in p_df.columns:
            p_df["avg_order_value"] = p_df["total_spend"].round(2)
        else:
            p_df["avg_order_value"] = 0.0

    # Ensure canonical CLV Value Band is present
    if "clv_band" not in p_df.columns:
        if "predicted_clv" in p_df.columns and p_df["predicted_clv"].nunique() > 1:
            q25, q50, q75 = p_df["predicted_clv"].quantile([0.25, 0.50, 0.75])
            p_df["clv_band"] = pd.cut(
                p_df["predicted_clv"],
                bins=[-np.inf, q25, q50, q75, np.inf],
                labels=["Bronze", "Silver", "Gold", "Platinum"],
            ).astype(str)
        else:
            p_df["clv_band"] = "Standard"

    return p_df.sort_values("priority_score", ascending=False).head(top_n)


def compute_quadrant_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """Segment customers into 4 strategic value-risk quadrants.

    Axes:
        X = Churn Probability (Split at 0.50)
        Y = Predicted CLV (Split at Median CLV)
    """
    if df is None or df.empty:
        return {}

    median_clv = df["predicted_clv"].median()
    churn_threshold = 0.50

    q_protect = df[(df["churn_probability"] >= churn_threshold) & (df["predicted_clv"] >= median_clv)]  # High Value, High Risk
    q_nurture = df[(df["churn_probability"] < churn_threshold) & (df["predicted_clv"] >= median_clv)]  # High Value, Low Risk
    q_reengage = df[(df["churn_probability"] >= churn_threshold) & (df["predicted_clv"] < median_clv)]  # Low Value, High Risk
    q_monitor = df[(df["churn_probability"] < churn_threshold) & (df["predicted_clv"] < median_clv)]  # Low Value, Low Risk

    total = len(df)
    return {
        "median_clv": median_clv,
        "churn_threshold": churn_threshold,
        "quadrants": {
            "Priority Protect (High Value, High Risk)": {
                "count": len(q_protect),
                "share": len(q_protect) / max(1, total),
                "revenue": q_protect["total_spend"].sum(),
                "action": "Immediate high-touch outreach, custom retention offer, logistics friction audit.",
                "badge_color": "#DC2626",
            },
            "Advocate & Nurture (High Value, Low Risk)": {
                "count": len(q_nurture),
                "share": len(q_nurture) / max(1, total),
                "revenue": q_nurture["total_spend"].sum(),
                "action": "VIP appreciation rewards, exclusive product previews, premium cross-sell.",
                "badge_color": "#16A34A",
            },
            "Automated Re-Engage (Low Value, High Risk)": {
                "count": len(q_reengage),
                "share": len(q_reengage) / max(1, total),
                "revenue": q_reengage["total_spend"].sum(),
                "action": "Automated email win-back campaign with seasonal discount promotion.",
                "badge_color": "#F59E0B",
            },
            "Standard Monitor (Low Value, Low Risk)": {
                "count": len(q_monitor),
                "share": len(q_monitor) / max(1, total),
                "revenue": q_monitor["total_spend"].sum(),
                "action": "Standard lifecycle nurture workflows and product discovery recommendations.",
                "badge_color": "#0284C7",
            },
        },
    }
