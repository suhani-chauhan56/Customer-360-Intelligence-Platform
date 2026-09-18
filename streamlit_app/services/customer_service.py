"""Customer Domain Service for CustomerAtlas.

Provides customer retrieval, health score normalization, lifecycle journey
derivation, risk indicator diagnostics, and comparison data extraction.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from utils.formatting import format_brl, format_pct


def get_customer_profile(df: pd.DataFrame, customer_id: str) -> Optional[pd.Series]:
    """Retrieve canonical customer record by customer_id."""
    if df is None or df.empty or not customer_id:
        return None
    matches = df[df["customer_id"].astype(str) == str(customer_id)]
    if matches.empty:
        return None
    return matches.iloc[0]


def search_customers(
    df: pd.DataFrame,
    search_query: str = "",
    segment: str = "All",
    risk_level: str = "All",
    state: str = "All",
    clv_band: str = "All",
    recency_filter: str = "All",
) -> pd.DataFrame:
    """Filter and search customer dataset with multi-criteria filters."""
    if df is None or df.empty:
        return pd.DataFrame()

    res = df.copy()

    # Search by customer_id or city
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        res = res[
            res["customer_id"].astype(str).str.lower().str.contains(q, na=False)
            | res.get("city", pd.Series("", index=res.index)).astype(str).str.lower().str.contains(q, na=False)
        ]

    # Filter by RFM Segment
    if segment != "All" and "rfm_segment" in res.columns:
        res = res[res["rfm_segment"] == segment]

    # Filter by Risk Level
    if risk_level != "All" and "churn_probability" in res.columns:
        if risk_level == "High Risk (>=65%)":
            res = res[res["churn_probability"] >= 0.65]
        elif risk_level == "Medium Risk (35-65%)":
            res = res[(res["churn_probability"] >= 0.35) & (res["churn_probability"] < 0.65)]
        elif risk_level == "Low Risk (<35%)":
            res = res[res["churn_probability"] < 0.35]

    # Filter by State
    if state != "All" and "state" in res.columns:
        res = res[res["state"] == state]

    # Filter by CLV Band
    if clv_band != "All" and "clv_band" in res.columns:
        res = res[res["clv_band"] == clv_band]

    # Filter by Recency
    if recency_filter != "All" and "recency_days" in res.columns:
        if recency_filter == "Recent (<90 days)":
            res = res[res["recency_days"] < 90]
        elif recency_filter == "Active (90-180 days)":
            res = res[(res["recency_days"] >= 90) & (res["recency_days"] <= 180)]
        elif recency_filter == "Lapsed (181-365 days)":
            res = res[(res["recency_days"] > 180) & (res["recency_days"] <= 365)]
        elif recency_filter == "Inactive (>365 days)":
            res = res[res["recency_days"] > 365]

    return res


def compute_customer_health(profile: pd.Series) -> List[Dict[str, Any]]:
    """Compute normalized health indicators across 6 core operational dimensions.

    Uses real normalized values from the customer record rather than arbitrary scores.
    """
    recency_days = float(profile.get("recency_days", 300))
    orders = int(profile.get("total_orders", 1))
    spend = float(profile.get("total_spend", 0))
    web_score = float(profile.get("web_engagement_score", 0))
    csat = float(profile.get("avg_review_score", 5.0))
    churn_prob = float(profile.get("churn_probability", 0.5))

    # Recency Health
    if recency_days <= 60:
        rec_label, rec_status, rec_color = "High (Active)", "Recent order within 60 days", "#16A34A"
    elif recency_days <= 180:
        rec_label, rec_status, rec_color = "Moderate", f"Last order {int(recency_days)} days ago", "#F59E0B"
    else:
        rec_label, rec_status, rec_color = "At Risk (Inactive)", f"Inactive for {int(recency_days)} days", "#DC2626"

    # Frequency Health
    if orders >= 3:
        freq_label, freq_status, freq_color = "Excellent", f"{orders} completed orders (Repeat)", "#16A34A"
    elif orders == 2:
        freq_label, freq_status, freq_color = "Strong", "2 completed orders (Repeat buyer)", "#0284C7"
    else:
        freq_label, freq_status, freq_color = "Standard", "1 single purchase completed", "#64748B"

    # Monetary Health
    if spend >= 500:
        mon_label, mon_status, mon_color = "Top Tier", f"{format_brl(spend)} lifetime spend", "#16A34A"
    elif spend >= 150:
        mon_label, mon_status, mon_color = "Healthy", f"{format_brl(spend)} lifetime spend", "#0284C7"
    else:
        mon_label, mon_status, mon_color = "Modest", f"{format_brl(spend)} lifetime spend", "#64748B"

    # Engagement Health
    if web_score >= 50:
        eng_label, eng_status, eng_color = "High", f"{web_score:.1f} digital engagement points", "#16A34A"
    elif web_score >= 20:
        eng_label, eng_status, eng_color = "Moderate", f"{web_score:.1f} digital engagement points", "#0284C7"
    else:
        eng_label, eng_status, eng_color = "Low / Passive", f"{web_score:.1f} digital engagement points", "#94A3B8"

    # CSAT / Sentiment Health
    if csat >= 4.5:
        sent_label, sent_status, sent_color = "Positive (5/5)", f"{csat:.1f} average review score", "#16A34A"
    elif csat >= 3.0:
        sent_label, sent_status, sent_color = "Neutral (3-4/5)", f"{csat:.1f} average review score", "#F59E0B"
    else:
        sent_label, sent_status, sent_color = "Negative (<3/5)", f"{csat:.1f} average review score", "#DC2626"

    # Churn Risk
    if churn_prob < 0.35:
        risk_label, risk_status, risk_color = "Low Risk", f"{format_pct(churn_prob)} propensity", "#16A34A"
    elif churn_prob < 0.65:
        risk_label, risk_status, risk_color = "Medium Risk", f"{format_pct(churn_prob)} propensity", "#F59E0B"
    else:
        risk_label, risk_status, risk_color = "High Risk", f"{format_pct(churn_prob)} propensity", "#DC2626"

    return [
        {"dimension": "Purchase Recency", "rating": rec_label, "detail": rec_status, "color": rec_color, "icon": "⏱️"},
        {"dimension": "Order Frequency", "rating": freq_label, "detail": freq_status, "color": freq_color, "icon": "📦"},
        {"dimension": "Monetary Value", "rating": mon_label, "detail": mon_status, "color": mon_color, "icon": "💰"},
        {"dimension": "Digital Engagement", "rating": eng_label, "detail": eng_status, "color": eng_color, "icon": "🌐"},
        {"dimension": "Feedback & CSAT", "rating": sent_label, "detail": sent_status, "color": sent_color, "icon": "⭐"},
        {"dimension": "Retention Health", "rating": risk_label, "detail": risk_status, "color": risk_color, "icon": "🎯"},
    ]


def derive_lifecycle_stages(profile: pd.Series) -> List[Dict[str, Any]]:
    """Derive verifiable lifecycle milestone stages based on the customer record."""
    first_date = profile.get("first_purchase_date")
    last_date = profile.get("last_purchase_date")
    orders = int(profile.get("total_orders", 1))
    spend = float(profile.get("total_spend", 0))
    segment = str(profile.get("rfm_segment", "Regular Customers"))
    clv_band = str(profile.get("clv_band", "Bronze"))

    first_date_str = pd.to_datetime(first_date).strftime("%b %d, %Y") if pd.notna(first_date) else "Recorded"
    last_date_str = pd.to_datetime(last_date).strftime("%b %d, %Y") if pd.notna(last_date) else "Recorded"

    stages = [
        {
            "stage": "First Purchase",
            "reached": True,
            "date": first_date_str,
            "description": f"Initial order recorded ({profile.get('favorite_category', 'General')})",
        },
        {
            "stage": "Repeat Purchase",
            "reached": orders > 1,
            "date": last_date_str if orders > 1 else "Not yet reached",
            "description": f"{orders} total orders completed" if orders > 1 else "Single transaction customer",
        },
        {
            "stage": "Loyal Customer Status",
            "reached": segment in {"Champions", "Loyal Customers"} or orders >= 3,
            "date": "Active" if (segment in {"Champions", "Loyal Customers"} or orders >= 3) else "Not yet reached",
            "description": f"RFM Segment: {segment}",
        },
        {
            "stage": "High-Value Tier",
            "reached": spend >= 300 or clv_band in {"Platinum", "Gold"},
            "date": f"Tier: {clv_band}",
            "description": f"Lifetime Spend: {format_brl(spend)}",
        },
        {
            "stage": "Current Lifecycle Segment",
            "reached": True,
            "date": f"Segment: {segment}",
            "description": f"Cluster: {profile.get('cluster_segment', 'Standard')}",
        },
    ]
    return stages


def diagnose_customer_risk_factors(profile: pd.Series) -> Dict[str, Any]:
    """Diagnose factual risk indicators for an individual customer.

    Uses specific indicators rather than fabricated explanations.
    """
    recency_days = float(profile.get("recency_days", 0))
    orders = int(profile.get("total_orders", 1))
    csat = float(profile.get("avg_review_score", 5.0))
    spend = float(profile.get("total_spend", 0))
    web_score = float(profile.get("web_engagement_score", 0))
    churn_prob = float(profile.get("churn_probability", 0))

    risk_factors = []
    protective_factors = []

    # Check recency
    if recency_days > 365:
        risk_factors.append(f"Extended inactivity: {int(recency_days)} days since last purchase (>1 year)")
    elif recency_days > 180:
        risk_factors.append(f"Lapsed purchase recency: {int(recency_days)} days inactive (>6 months)")
    else:
        protective_factors.append(f"Recent purchase activity: {int(recency_days)} days ago")

    # Check order frequency
    if orders == 1:
        risk_factors.append("Single-purchase customer (no repeat order history established)")
    else:
        protective_factors.append(f"Repeat purchase history established ({orders} completed orders)")

    # Check CSAT review
    if csat <= 2.0:
        risk_factors.append(f"Low satisfaction signal: Average rating of {csat:.1f} / 5.0 stars")
    elif csat >= 4.0:
        protective_factors.append(f"Positive customer feedback: Average rating of {csat:.1f} / 5.0 stars")

    # Check digital engagement
    if web_score < 10:
        risk_factors.append("Low recent digital touchpoint engagement")
    elif web_score >= 40:
        protective_factors.append("Active digital web browsing session footprint")

    # Check high monetary exposure
    if spend >= 400:
        exposure_note = f"High revenue at risk: {format_brl(spend)} lifetime merchandise spend"
    else:
        exposure_note = f"Standard value exposure: {format_brl(spend)} lifetime spend"

    risk_level = "High Risk" if churn_prob >= 0.65 else "Medium Risk" if churn_prob >= 0.35 else "Low Risk"

    return {
        "risk_level": risk_level,
        "churn_probability": churn_prob,
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "exposure_note": exposure_note,
    }


def explain_rfm_segment(profile: pd.Series) -> Dict[str, Any]:
    """Provide transparent data factors leading to the customer's RFM classification."""
    segment = str(profile.get("rfm_segment", "Regular Customers"))
    r_score = int(profile.get("r_score", 1))
    f_score = int(profile.get("f_score", 1))
    m_score = int(profile.get("m_score", 1))
    recency = int(profile.get("recency_days", 0))
    orders = int(profile.get("total_orders", 1))
    spend = float(profile.get("total_spend", 0))

    factors = [
        f"Recency Score {r_score}/5 (Purchased {recency} days ago)",
        f"Frequency Score {f_score}/5 ({orders} completed order{'s' if orders > 1 else ''})",
        f"Monetary Score {m_score}/5 ({format_brl(spend)} total lifetime spend)",
    ]

    descriptions = {
        "Champions": "Top-tier customers with recent purchases, frequent orders, and highest monetary spending.",
        "Loyal Customers": "Consistent repeat buyers with high lifetime spend and dependable purchase intervals.",
        "Potential Loyalists": "Recent purchasers with good initial spend who show high potential for repeat conversion.",
        "Regular Customers": "Standard baseline customers with average recency, order frequency, and transaction sizes.",
        "At Risk": "Previously active customers who have not made a purchase recently and require re-engagement.",
        "Lost Customers": "Longest inactive customers with lowest recency scores who have likely churned.",
    }

    return {
        "segment": segment,
        "rfm_code": f"R:{r_score} | F:{f_score} | M:{m_score}",
        "explanation": descriptions.get(segment, "Customer classified based on quintile RFM matrix scoring."),
        "factors": factors,
    }
