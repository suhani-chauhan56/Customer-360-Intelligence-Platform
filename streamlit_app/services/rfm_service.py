"""RFM Intelligence and Segmentation Service for CustomerAtlas.

Provides aggregated RFM metrics, segment distribution analytics, segment
comparison matrices, and distribution metrics.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from utils.formatting import format_brl, format_num, format_pct


def compute_rfm_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate overall portfolio RFM averages and summary benchmarks."""
    if df is None or df.empty:
        return {
            "avg_recency": 0.0,
            "avg_frequency": 0.0,
            "avg_monetary": 0.0,
            "median_recency": 0.0,
            "median_monetary": 0.0,
            "total_customers": 0,
        }

    return {
        "avg_recency": float(df["recency_days"].mean()),
        "avg_frequency": float(df["total_orders"].mean()),
        "avg_monetary": float(df["total_spend"].mean()),
        "median_recency": float(df["recency_days"].median()),
        "median_monetary": float(df["total_spend"].median()),
        "total_customers": int(len(df)),
    }


def compute_segment_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Compute detailed segment breakdown with counts, shares, and averages."""
    if df is None or df.empty or "rfm_segment" not in df.columns:
        return pd.DataFrame()

    total_cust = len(df)
    total_rev = df["total_spend"].sum()

    agg = (
        df.groupby("rfm_segment", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            total_revenue=("total_spend", "sum"),
            avg_spend=("total_spend", "mean"),
            avg_clv=("predicted_clv", "mean"),
            avg_orders=("total_orders", "mean"),
            avg_recency=("recency_days", "mean"),
            avg_aov=("avg_order_value", "mean"),
            avg_churn_prob=("churn_probability", "mean"),
        )
    )

    agg["customer_share"] = agg["customers"] / max(1, total_cust)
    agg["revenue_share"] = agg["total_revenue"] / max(1, total_rev)

    # Sort logically by revenue or customers
    return agg.sort_values("total_revenue", ascending=False)


def compare_segments(df: pd.DataFrame, segment_a: str, segment_b: str) -> List[Dict[str, Any]]:
    """Compare two RFM segments across key analytical dimensions."""
    if df is None or df.empty:
        return []

    sub_a = df[df["rfm_segment"] == segment_a]
    sub_b = df[df["rfm_segment"] == segment_b]

    total_base = len(df)
    total_gmv = df["total_spend"].sum()

    def get_metrics(sub: pd.DataFrame) -> Dict[str, Any]:
        if sub.empty:
            return {
                "count": 0,
                "share": 0.0,
                "revenue": 0.0,
                "rev_share": 0.0,
                "avg_clv": 0.0,
                "avg_orders": 0.0,
                "avg_recency": 0.0,
                "avg_aov": 0.0,
                "churn_rate": 0.0,
                "avg_csat": 0.0,
            }
        return {
            "count": len(sub),
            "share": len(sub) / max(1, total_base),
            "revenue": sub["total_spend"].sum(),
            "rev_share": sub["total_spend"].sum() / max(1, total_gmv),
            "avg_clv": sub["predicted_clv"].mean(),
            "avg_orders": sub["total_orders"].mean(),
            "avg_recency": sub["recency_days"].mean(),
            "avg_aov": sub["avg_order_value"].mean(),
            "churn_rate": sub["churn_probability"].mean(),
            "avg_csat": sub.get("avg_review_score", pd.Series(5.0, index=sub.index)).mean(),
        }

    m_a = get_metrics(sub_a)
    m_b = get_metrics(sub_b)

    return [
        {
            "metric": "Customer Count",
            "val_a": f"{m_a['count']:,} ({format_pct(m_a['share'])})",
            "val_b": f"{m_b['count']:,} ({format_pct(m_b['share'])})",
        },
        {
            "metric": "Total Revenue (GMV)",
            "val_a": f"{format_brl(m_a['revenue'])} ({format_pct(m_a['rev_share'])})",
            "val_b": f"{format_brl(m_b['revenue'])} ({format_pct(m_b['rev_share'])})",
        },
        {
            "metric": "Average 12M CLV",
            "val_a": format_brl(m_a["avg_clv"]),
            "val_b": format_brl(m_b["avg_clv"]),
        },
        {
            "metric": "Average Order Count",
            "val_a": f"{m_a['avg_orders']:.2f} orders",
            "val_b": f"{m_b['avg_orders']:.2f} orders",
        },
        {
            "metric": "Average Inactivity (Recency)",
            "val_a": f"{m_a['avg_recency']:.0f} days",
            "val_b": f"{m_b['avg_recency']:.0f} days",
        },
        {
            "metric": "Average Order Value (AOV)",
            "val_a": format_brl(m_a["avg_aov"]),
            "val_b": format_brl(m_b["avg_aov"]),
        },
        {
            "metric": "Average Churn Propensity",
            "val_a": format_pct(m_a["churn_rate"]),
            "val_b": format_pct(m_b["churn_rate"]),
        },
        {
            "metric": "Average CSAT Review Rating",
            "val_a": f"{m_a['avg_csat']:.2f} / 5.0",
            "val_b": f"{m_b['avg_csat']:.2f} / 5.0",
        },
    ]


def get_segment_playbook(segment_name: str) -> Dict[str, Any]:
    """Retrieve actionable strategic playbook and focus areas for an RFM segment."""
    playbooks = {
        "Champions": {
            "title": "Champions Retention & VIP Advocacy",
            "priority": "Highest Commercial Priority",
            "badge_color": "#16A34A",
            "summary": "Your most valuable and engaged customers with recent high-value purchases.",
            "actions": [
                "Reward loyalty with early access to new product catalog drops.",
                "Offer exclusive VIP perks, dedicated concierge support, and milestone rewards.",
                "Cross-sell premium complementary categories with personalized bundles.",
            ],
        },
        "Loyal Customers": {
            "title": "Loyal Customer Value Maximization",
            "priority": "High Commercial Priority",
            "badge_color": "#0284C7",
            "summary": "Dependable repeat purchasers who form the core revenue backbone.",
            "actions": [
                "Implement tiered loyalty rewards to incentivize progression to Champion status.",
                "Recommend higher-value variants and seasonal merchandise.",
                "Engage with feedback requests and Voice of Customer surveys.",
            ],
        },
        "Potential Loyalists": {
            "title": "Potential Loyalist Conversion & Nurturing",
            "priority": "Growth Opportunity",
            "badge_color": "#8B5CF6",
            "summary": "Recent buyers with solid initial spend who need encouragement to build a repeat habit.",
            "actions": [
                "Trigger automated post-purchase second-order onboarding workflows.",
                "Provide targeted category recommendations based on initial purchase.",
                "Offer time-limited free shipping or bundle savings on their next order.",
            ],
        },
        "Regular Customers": {
            "title": "Regular Customer Engagement & Activation",
            "priority": "Standard Baseline",
            "badge_color": "#4F46E5",
            "summary": "Moderate frequency and spending customers who maintain steady baseline demand.",
            "actions": [
                "Personalize marketing touchpoints according to favorite product category.",
                "Deploy seasonal promotional campaigns to increase purchase velocity.",
                "Promote high-rated cross-sell categories with positive review social proof.",
            ],
        },
        "At Risk": {
            "title": "At-Risk Customer Win-Back Campaign",
            "priority": "Urgent Attention Required",
            "badge_color": "#F59E0B",
            "summary": "Valuable customers whose purchase frequency has dropped and recency has extended.",
            "actions": [
                "Launch personalized win-back re-engagement email sequence with incentives.",
                "Audit logistics satisfaction and resolve recurring fulfillment bottlenecks.",
                "Re-engage with dynamic new arrivals in previously purchased categories.",
            ],
        },
        "Lost Customers": {
            "title": "Lost Customer Diagnostics & Revival",
            "priority": "Low Touch / Selective Reactivation",
            "badge_color": "#DC2626",
            "summary": "Longest inactive customers with low recent engagement.",
            "actions": [
                "Run low-cost automated revival campaigns during major seasonal clearance events.",
                "Collect exit feedback to diagnose root causes of customer churn.",
                "Filter unengaged contacts to optimize marketing campaign deliverability.",
            ],
        },
    }
    return playbooks.get(
        segment_name,
        {
            "title": f"{segment_name} Strategy",
            "priority": "General Strategy",
            "badge_color": "#64748B",
            "summary": "Audience segment based on RFM analytical scoring.",
            "actions": ["Monitor purchase cadence and apply category-specific marketing."],
        },
    )
