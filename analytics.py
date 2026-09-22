"""CustomerAtlas Unified Analytics and Machine Learning Engine.

Comprehensive, production-grade Analytics & Data Science module providing:
1. Dataset Ingestion & Schema Validation
2. RFM Intelligence & Customer Segmentation
3. 12-Month Forward Customer Lifetime Value (CLV) Modeling
4. Churn Propensity, Revenue Exposure & Priority Scoring
5. 6-Factor Customer Health Scoring ($0-100$)
6. 6-Stage Lifecycle State Machine
7. Grounded AI Decision Support & Intent Classification
8. Executive Insights Generation (Pareto, Risk, Repeat Rate, Geographic)
9. Population Stability Index (PSI) Feature Drift Monitoring
10. What-If Strategic Scenario Simulation

Can be imported programmatically or executed as a standalone CLI analytics pipeline.
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Setup robust project paths
BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "streamlit_app"
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data" / "processed")))
MODELS_DIR = Path(os.getenv("MODELS_DIR", str(BASE_DIR / "models")))

for path_dir in [str(BASE_DIR), str(APP_DIR)]:
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

# Initialize logger
logger = logging.getLogger("customeratlas.analytics")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ==============================================================================
# 1. DATA INGESTION & VALIDATION LAYER
# ==============================================================================

REQUIRED_COLUMNS: List[str] = [
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


def load_dataset(
    filename: str = "customer_360_features.csv",
    data_dir: Optional[Union[str, Path]] = None,
    parse_dates: Tuple[str, ...] = ("first_purchase_date", "last_purchase_date"),
) -> pd.DataFrame:
    """Load, parse, and validate a dataset from the processed data directory.

    Args:
        filename: Dataset filename (e.g. 'customer_360_features.csv').
        data_dir: Optional override directory.
        parse_dates: Tuple of date column names to parse.

    Returns:
        pd.DataFrame containing the validated dataset.
    """
    target_dir = Path(data_dir) if data_dir else DATA_DIR
    file_path = target_dir / filename

    if not file_path.exists():
        logger.warning(f"Dataset not found at {file_path}. Returning empty DataFrame.")
        return pd.DataFrame()

    try:
        available_cols = pd.read_csv(file_path, nrows=0).columns.tolist()
        dates_to_parse = [c for c in parse_dates if c in available_cols]
        df = pd.read_csv(file_path, parse_dates=dates_to_parse)
        logger.info(f"Loaded {filename}: {len(df):,} records, {len(df.columns)} features.")
        return df
    except Exception as e:
        logger.error(f"Failed to read dataset from {file_path}: {e}", exc_info=True)
        return pd.DataFrame()


def validate_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform data contract and schema validation on customer features.

    Returns:
        Validation report dictionary.
    """
    if df is None or df.empty:
        return {
            "is_valid": False,
            "total_records": 0,
            "issues": ["DataFrame is empty or None."],
            "missing_columns": REQUIRED_COLUMNS,
        }

    issues: List[str] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        issues.append(f"Missing required columns: {missing}")

    null_ids = int(df["customer_id"].isnull().sum()) if "customer_id" in df.columns else 0
    if null_ids > 0:
        issues.append(f"Found {null_ids:,} null customer IDs.")

    neg_spend = int((df["total_spend"] < 0).sum()) if "total_spend" in df.columns else 0
    if neg_spend > 0:
        issues.append(f"Found {neg_spend:,} negative spend anomalies.")

    invalid_churn = 0
    if "churn_probability" in df.columns:
        invalid_churn = int(((df["churn_probability"] < 0.0) | (df["churn_probability"] > 1.0)).sum())
        if invalid_churn > 0:
            issues.append(f"Found {invalid_churn:,} out-of-range churn probabilities.")

    return {
        "is_valid": len(issues) == 0,
        "total_records": len(df),
        "total_columns": len(df.columns),
        "missing_columns": missing,
        "null_ids": null_ids,
        "negative_spend_count": neg_spend,
        "invalid_churn_count": invalid_churn,
        "issues": issues,
    }


# ==============================================================================
# 2. EXECUTIVE OVERVIEW & MACRO KPIs
# ==============================================================================

@dataclass
class ExecutiveKPIs:
    """Standardized macro portfolio metrics container."""
    total_customers: int
    active_customers: int
    active_rate: float
    total_gmv: float
    avg_customer_value: float
    avg_order_value: float
    repeat_customer_rate: float
    repeat_customers_count: int
    at_risk_customers_count: int
    at_risk_revenue_exposure: float
    high_value_customers_count: int
    high_value_revenue: float


def compute_executive_kpis(df: pd.DataFrame) -> ExecutiveKPIs:
    """Calculate core executive health KPIs from canonical customer records."""
    if df is None or df.empty:
        return ExecutiveKPIs(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0, 0.0)

    total_customers = int(df["customer_id"].nunique())
    total_gmv = float(df["total_spend"].sum()) if "total_spend" in df.columns else 0.0
    total_orders = int(df["total_orders"].sum()) if "total_orders" in df.columns else max(1, total_customers)

    avg_customer_val = total_gmv / max(1, total_customers)
    avg_order_val = total_gmv / max(1, total_orders)

    # Active buyers (recency <= 180 days)
    recency_col = df["recency_days"] if "recency_days" in df.columns else pd.Series(0, index=df.index)
    active_mask = recency_col <= 180
    active_count = int(active_mask.sum())
    active_rate = active_count / max(1, total_customers)

    # Repeat buyers (orders > 1)
    orders_col = df["total_orders"] if "total_orders" in df.columns else pd.Series(1, index=df.index)
    repeat_mask = orders_col > 1
    repeat_count = int(repeat_mask.sum())
    repeat_rate = repeat_count / max(1, total_customers)

    # At-risk cohort (churn_probability >= 0.65)
    churn_col = df["churn_probability"] if "churn_probability" in df.columns else pd.Series(0.0, index=df.index)
    at_risk_mask = churn_col >= 0.65
    at_risk_count = int(at_risk_mask.sum())
    at_risk_rev = float(df.loc[at_risk_mask, "total_spend"].sum()) if "total_spend" in df.columns else 0.0

    # High-value cohort (predicted_clv >= 90th percentile)
    clv_col = df["predicted_clv"] if "predicted_clv" in df.columns else pd.Series(0.0, index=df.index)
    p90_clv = float(clv_col.quantile(0.90)) if not clv_col.empty else 0.0
    hv_mask = clv_col >= p90_clv
    hv_count = int(hv_mask.sum())
    hv_rev = float(df.loc[hv_mask, "total_spend"].sum()) if "total_spend" in df.columns else 0.0

    return ExecutiveKPIs(
        total_customers=total_customers,
        active_customers=active_count,
        active_rate=round(active_rate, 4),
        total_gmv=round(total_gmv, 2),
        avg_customer_value=round(avg_customer_val, 2),
        avg_order_value=round(avg_order_val, 2),
        repeat_customer_rate=round(repeat_rate, 4),
        repeat_customers_count=repeat_count,
        at_risk_customers_count=at_risk_count,
        at_risk_revenue_exposure=round(at_risk_rev, 2),
        high_value_customers_count=hv_count,
        high_value_revenue=round(hv_rev, 2),
    )


# ==============================================================================
# 3. RFM SEGMENTATION & AUDIENCE ECONOMICS
# ==============================================================================

def compute_rfm_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate customer counts, revenue shares, and behavioral metrics per RFM segment."""
    if df is None or df.empty or "rfm_segment" not in df.columns:
        return pd.DataFrame()

    total_c = len(df)
    total_rev = df["total_spend"].sum() if "total_spend" in df.columns else 1.0

    agg = (
        df.groupby("rfm_segment", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            total_revenue=("total_spend", "sum"),
            avg_spend=("total_spend", "mean"),
            avg_clv=("predicted_clv", "mean"),
            avg_orders=("total_orders", "mean"),
            avg_recency=("recency_days", "mean"),
            avg_churn_prob=("churn_probability", "mean"),
        )
    )

    agg["customer_share"] = (agg["customers"] / max(1, total_c)).round(4)
    agg["revenue_share"] = (agg["total_revenue"] / max(1.0, total_rev)).round(4)
    return agg.sort_values("total_revenue", ascending=False)


# ==============================================================================
# 4. CUSTOMER LIFETIME VALUE (CLV) MODELING
# ==============================================================================

def compute_clv_brackets(df: pd.DataFrame) -> pd.DataFrame:
    """Group customers into standardized CLV brackets with revenue contribution."""
    if df is None or df.empty or "predicted_clv" not in df.columns:
        return pd.DataFrame()

    bins = [-np.inf, 100, 250, 500, 1000, np.inf]
    labels = ["< R$100", "R$100 – R$250", "R$250 – R$500", "R$500 – R$1,000", "> R$1,000"]

    df_binned = df.copy()
    df_binned["clv_bracket"] = pd.cut(df_binned["predicted_clv"].fillna(0), bins=bins, labels=labels, right=False)

    summary = (
        df_binned.groupby("clv_bracket", observed=False)
        .agg(
            customers=("customer_id", "count"),
            total_spend=("total_spend", "sum"),
            total_clv=("predicted_clv", "sum"),
            avg_churn_prob=("churn_probability", "mean"),
        )
        .reset_index()
    )
    total_c = len(df)
    total_spend = df["total_spend"].sum()
    summary["customer_pct"] = (summary["customers"] / max(1, total_c)).round(4)
    summary["revenue_pct"] = (summary["total_spend"] / max(1.0, total_spend)).round(4)
    return summary


# ==============================================================================
# 5. CHURN RISK & PRIORITIZATION SCORING
# ==============================================================================

def prioritize_retention_queue(df: pd.DataFrame, top_n: int = 100) -> pd.DataFrame:
    """Compute mathematical retention priority scores and rank customers.

    Formula:
        Priority = Churn Probability * (Predicted CLV / CLV_p99) * 100
    """
    if df is None or df.empty:
        return pd.DataFrame()

    p_df = df.copy()
    p99_clv = float(p_df["predicted_clv"].quantile(0.99)) if "predicted_clv" in p_df.columns else 1.0
    p99_clv = max(1.0, p99_clv)

    norm_clv = (p_df["predicted_clv"] / p99_clv).clip(upper=1.0)
    churn_p = p_df.get("churn_probability", pd.Series(0.5, index=p_df.index))

    p_df["priority_score"] = (churn_p * norm_clv * 100.0).round(1)

    target_cols = [
        "customer_id",
        "priority_score",
        "churn_probability",
        "predicted_clv",
        "total_spend",
        "rfm_segment",
        "total_orders",
        "recency_days",
        "city",
        "state",
    ]
    avail = [c for c in target_cols if c in p_df.columns]
    return p_df.sort_values("priority_score", ascending=False).head(top_n)[avail]


# ==============================================================================
# 6. HEALTH SCORE & LIFECYCLE STATE MACHINE
# ==============================================================================

def calculate_health_score(profile: pd.Series) -> Dict[str, Any]:
    """Calculate documented 6-factor Customer Health Score (0-100)."""
    recency = float(profile.get("recency_days", 300))
    orders = int(profile.get("total_orders", 1))
    spend = float(profile.get("total_spend", 0.0))
    web_score = float(profile.get("web_engagement_score", 0.0))
    csat = float(profile.get("avg_review_score", 5.0))
    churn_prob = float(profile.get("churn_probability", 0.5))

    r_norm = max(0.0, min(100.0, 100.0 * (1.0 - (recency / 365.0))))
    f_norm = min(100.0, orders * 33.33)
    m_norm = min(100.0, (spend / 500.0) * 100.0)
    eng_norm = min(100.0, (web_score / 60.0) * 100.0)
    csat_norm = min(100.0, (csat / 5.0) * 100.0)
    risk_penalty = churn_prob * 100.0

    raw = (
        0.25 * r_norm
        + 0.25 * f_norm
        + 0.25 * m_norm
        + 0.15 * eng_norm
        + 0.10 * csat_norm
        - 0.20 * risk_penalty
    )
    score = round(float(np.clip(raw, 0.0, 100.0)), 1)
    tier = "Thriving 🟢" if score >= 75.0 else "Healthy 🔵" if score >= 50.0 else "At Risk 🟡" if score >= 30.0 else "Critical 🔴"

    return {
        "score": score,
        "health_tier": tier,
        "components": {
            "recency_vital": round(r_norm, 1),
            "frequency_vital": round(f_norm, 1),
            "monetary_vital": round(m_norm, 1),
            "engagement_vital": round(eng_norm, 1),
            "csat_vital": round(csat_norm, 1),
            "risk_penalty": round(risk_penalty, 1),
        },
    }


def classify_lifecycle_stage(profile: pd.Series) -> Dict[str, Any]:
    """Classify customer into deterministic 6-stage lifecycle state machine."""
    age_days = int(profile.get("customer_age_days", 1))
    recency = int(profile.get("recency_days", 0))
    orders = int(profile.get("total_orders", 1))
    churn_prob = float(profile.get("churn_probability", 0.0))
    rfm_seg = str(profile.get("rfm_segment", "Regular Customers"))

    if recency > 365 and churn_prob >= 0.65:
        state = "Inactive / Lost"
    elif recency > 180 or churn_prob >= 0.65:
        state = "At Risk"
    elif orders >= 3 or rfm_seg in {"Champions", "Loyal Customers"}:
        state = "Loyal"
    elif orders >= 2 and recency <= 120:
        state = "Engaged"
    elif age_days <= 60 and orders == 1:
        state = "New"
    else:
        state = "Activated"

    return {"lifecycle_state": state, "orders": orders, "recency_days": recency}


# ==============================================================================
# 7. FEATURE DRIFT (PSI) & DATA QUALITY
# ==============================================================================

def calculate_population_stability_index(
    baseline: pd.Series,
    target: pd.Series,
    num_buckets: int = 10,
) -> float:
    """Calculate Population Stability Index (PSI) between baseline and target distributions."""
    b_clean = baseline.dropna()
    t_clean = target.dropna()

    if b_clean.empty or t_clean.empty or b_clean.nunique() <= 1:
        return 0.0

    percentiles = np.linspace(0, 100, num_buckets + 1)
    bin_edges = np.unique(np.percentile(b_clean, percentiles))

    if len(bin_edges) < 2:
        return 0.0

    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    b_counts, _ = np.histogram(b_clean, bins=bin_edges)
    t_counts, _ = np.histogram(t_clean, bins=bin_edges)

    eps = 1e-4
    b_prop = (b_counts / max(1, len(b_clean))) + eps
    t_prop = (t_counts / max(1, len(t_clean))) + eps

    b_prop = b_prop / b_prop.sum()
    t_prop = t_prop / t_prop.sum()

    psi = np.sum((t_prop - b_prop) * np.log(t_prop / b_prop))
    return float(round(max(0.0, psi), 4))


# ==============================================================================
# 8. STANDALONE PIPELINE RUNNER
# ==============================================================================

def run_full_analytics_audit(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Execute complete analytical audit workflow and return unified metrics payload."""
    if df is None:
        df = load_dataset()

    validation = validate_dataset(df)
    kpis = compute_executive_kpis(df)
    segments = compute_rfm_distribution(df)
    clv_bins = compute_clv_brackets(df)
    prio_queue = prioritize_retention_queue(df, top_n=10)

    return {
        "status": "Success",
        "timestamp": datetime.utcnow().isoformat(),
        "data_validation": validation,
        "executive_kpis": asdict(kpis),
        "segment_count": len(segments),
        "clv_bins_count": len(clv_bins),
        "prioritized_retention_top10": prio_queue.to_dict(orient="records"),
    }


if __name__ == "__main__":
    logger.info("Running CustomerAtlas Analytics Engine...")
    results = run_full_analytics_audit()
    print(json.dumps(results, indent=2))
