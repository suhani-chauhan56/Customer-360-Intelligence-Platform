"""Customer Action Recommendation Engine Service for CustomerAtlas.

Implements a transparent, rule-grounded recommendation system combining:
1. Churn Risk & Retention Signals (Urgency & Retention Workflows)
2. RFM Segment Strategy (Loyalty Perks, VIP Concierge, Win-Back Sequences)
3. Customer Lifetime Value (Resource Allocation & Tiered Budgeting)
4. Feedback & CSAT Ratings (Voice of Customer & Service Recovery)
5. Product Affinity & Next-Best-Category Basket Association (Cross-Sell / Up-Sell)
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from config.settings import CACHE_TTL_SECONDS
from utils.formatting import format_brl, format_pct
from utils.logging_config import logger


# Documented business logic rules for action assignment
RECOMMENDATION_RULES: List[Dict[str, Any]] = [
    {
        "action_type": "VIP Retention Outreach",
        "priority": "Urgent",
        "badge_color": "#DC2626",
        "target_audience": "Champions & High CLV with Churn Risk >= 65%",
        "channel": "Dedicated Account Manager / VIP Concierge",
        "description": "Immediate white-glove contact, custom retention incentives, and logistics friction resolution.",
        "rationale": "High lifetime value is exposed to imminent churn; proactive white-glove outreach provides highest ROI.",
    },
    {
        "action_type": "Win-back Campaign",
        "priority": "High",
        "badge_color": "#EA580C",
        "target_audience": "At Risk / Lost Customers with Recency > 180 days",
        "channel": "Automated Personalized Email + Exclusive Re-activation Discount",
        "description": "Multi-touch automated email re-engagement sequence offering personalized discount in previous affinity category.",
        "rationale": "Lapsed customers require economic incentives and updated catalog exposure to re-enter the purchasing cycle.",
    },
    {
        "action_type": "Loyalty Reward & Advocacy",
        "priority": "High",
        "badge_color": "#16A34A",
        "target_audience": "Champions & Loyal Customers with CSAT >= 4.5 and Churn Risk < 35%",
        "channel": "Loyalty Program Tier Upgrade / Early Product Drops",
        "description": "Surprise-and-delight rewards, tier upgrade badges, and invitations to beta programs or review advocacy.",
        "rationale": "Deepens brand affinity, safeguards against competitive poaching, and drives organic word-of-mouth advocacy.",
    },
    {
        "action_type": "Second-Purchase Cross-Sell",
        "priority": "High",
        "badge_color": "#8B5CF6",
        "target_audience": "Potential Loyalists (1 completed order, Recency <= 90 days)",
        "channel": "Personalized Category Recommendation Workflow",
        "description": "Curated cross-sell bundle recommendations based on market basket co-occurrence within 14-30 days of first order.",
        "rationale": "Converting a 1-time buyer into a repeat customer increases expected 12-month CLV by over 2.5x.",
    },
    {
        "action_type": "Service Recovery & Feedback",
        "priority": "Urgent",
        "badge_color": "#E11D48",
        "target_audience": "Customers with CSAT Review <= 2.0 stars",
        "channel": "Customer Success Ticket & Quality Apology Voucher",
        "description": "Direct contact from support team to investigate fulfillment friction and offer store credit resolution.",
        "rationale": "Resolving customer complaints effectively can recover up to 70% of dissatisfied accounts.",
    },
    {
        "action_type": "Category Upsell & Basket Expansion",
        "priority": "Medium",
        "badge_color": "#0284C7",
        "target_audience": "Regular Customers with AOV below category average",
        "channel": "In-app Promos / Free Shipping Threshold Boosts",
        "description": "Tiered volume discounts (e.g. 'Add R$30 for Free Shipping') and complementary product bundles.",
        "rationale": "Drives immediate incremental order value without degrading gross margin.",
    },
    {
        "action_type": "Standard Lifecycle Nurture",
        "priority": "Standard",
        "badge_color": "#64748B",
        "target_audience": "Healthy baseline customers with low churn risk and moderate spend",
        "channel": "Standard Weekly Newsletter & New Arrivals Digest",
        "description": "Regular communication cadence highlighting trending new catalog arrivals in preferred categories.",
        "rationale": "Maintains brand top-of-mind recall at low marginal distribution cost.",
    },
]


def generate_customer_recommendation(profile: pd.Series) -> Dict[str, Any]:
    """Derive deterministic, explainable Next-Best-Action for a customer profile."""
    churn_prob = float(profile.get("churn_probability", 0.5))
    spend = float(profile.get("total_spend", 0.0))
    clv = float(profile.get("predicted_clv", 0.0))
    orders = int(profile.get("total_orders", 1))
    recency = int(profile.get("recency_days", 0))
    csat = float(profile.get("avg_review_score", 5.0))
    segment = str(profile.get("rfm_segment", "Regular Customers"))

    # Priority 1: Service Recovery for dissatisfied buyers
    if csat <= 2.0 and orders >= 1:
        rule = RECOMMENDATION_RULES[4]  # Service Recovery
        reason = f"Low CSAT rating ({csat:.1f}/5.0 stars). High friction risk requiring customer success outreach."
    
    # Priority 2: VIP Retention for high spend / high CLV at risk
    elif churn_prob >= 0.65 and (spend >= 250 or clv >= 300 or segment in {"Champions", "Loyal Customers"}):
        rule = RECOMMENDATION_RULES[0]  # VIP Retention
        reason = f"High Churn Risk ({format_pct(churn_prob)}) on High-Value Account ({format_brl(spend)} GMV, 12M CLV: {format_brl(clv)})."

    # Priority 3: Win-back for lapsed buyers
    elif (churn_prob >= 0.65 or recency > 180) and segment in {"At Risk", "Lost Customers", "Regular Customers"}:
        rule = RECOMMENDATION_RULES[1]  # Win-back
        reason = f"Extended inactivity ({recency} days). Requires economic win-back trigger."

    # Priority 4: Loyalty Reward for top advocates
    elif segment in {"Champions", "Loyal Customers"} and churn_prob < 0.35:
        rule = RECOMMENDATION_RULES[2]  # Loyalty Reward
        reason = f"Loyal Customer ({orders} orders, {format_brl(spend)}) with high health and low churn risk ({format_pct(churn_prob)})."

    # Priority 5: Second-Purchase Cross-Sell for recent new buyers
    elif orders == 1 and recency <= 90:
        rule = RECOMMENDATION_RULES[3]  # Second-Purchase Cross-Sell
        reason = f"Recent first purchase ({recency} days ago). Prime window to trigger repeat purchase nurturing."

    # Priority 6: Upsell for regular buyers
    elif orders >= 1 and spend >= 100:
        rule = RECOMMENDATION_RULES[5]  # Category Upsell
        reason = f"Active customer with baseline spend ({format_brl(spend)}). Opportunity for basket size expansion."

    # Default: Standard Lifecycle Nurture
    else:
        rule = RECOMMENDATION_RULES[6]  # Standard Lifecycle Nurture
        reason = "Stable baseline customer with normal purchase interval."

    return {
        "customer_id": str(profile.get("customer_id", "")),
        "action_type": rule["action_type"],
        "priority": rule["priority"],
        "badge_color": rule["badge_color"],
        "channel": rule["channel"],
        "reason": reason,
        "description": rule["description"],
        "rfm_segment": segment,
        "total_spend": spend,
        "total_orders": orders,
        "avg_order_value": float(profile.get("avg_order_value", spend / max(1, orders))),
        "clv_band": str(profile.get("clv_band", "Bronze")),
        "predicted_clv": clv,
        "churn_probability": churn_prob,
        "recency_days": recency,
        "avg_review_score": csat,
        "favorite_category": str(profile.get("favorite_category", "General")),
        "city": str(profile.get("city", "")),
        "state": str(profile.get("state", "")),
    }


def compute_recommendation_portfolio(df: pd.DataFrame, limit: int = 1000) -> pd.DataFrame:
    """Generate recommendations for all customer records in the filtered dataset."""
    if df is None or df.empty:
        return pd.DataFrame()

    sample_df = df.head(limit) if len(df) > limit else df
    recs = [generate_customer_recommendation(row) for _, row in sample_df.iterrows()]
    return pd.DataFrame(recs)


def compute_recommendation_summary(recs_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate recommendation distribution by action type and priority."""
    if recs_df is None or recs_df.empty:
        return pd.DataFrame()

    summary = (
        recs_df.groupby(["action_type", "priority", "badge_color"], as_index=False)
        .agg(
            customer_count=("customer_id", "count"),
            total_gmv=("total_spend", "sum"),
            avg_clv=("predicted_clv", "mean"),
            avg_churn_risk=("churn_probability", "mean"),
        )
        .sort_values("customer_count", ascending=False)
    )
    return summary
