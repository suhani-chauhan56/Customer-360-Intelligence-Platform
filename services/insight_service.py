"""Executive Insights and Business Intelligence Signals Service for CustomerAtlas.

Provides evidence-backed, deterministic structured insights derived from empirical
customer feature distributions, Pareto concentration, geographical demand hubs,
repeat purchase patterns, and churn risk exposures.
"""

from typing import Any, Dict, List
import pandas as pd

from utils.formatting import format_brl, format_pct


def generate_executive_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate deterministic, evidence-grounded executive insights from customer data.

    Calculates 4 core commercial signals:
    1. Revenue Concentration (Pareto Distribution)
    2. Regional Demand Hubs (Geographic Focus)
    3. Single-Purchase Drop-Off Opportunity (Retention Lever)
    4. Churn Risk Exposure & Capital Protection (Risk Exposure)
    """
    if df is None or df.empty:
        return []

    total_customers = int(df["customer_id"].nunique()) if "customer_id" in df.columns else len(df)
    total_gmv = float(df["total_spend"].sum()) if "total_spend" in df.columns else 0.0

    repeat_customers = int((df["total_orders"] > 1).sum()) if "total_orders" in df.columns else 0
    repeat_rate = repeat_customers / max(1, total_customers)

    at_risk_df = df[df["churn_probability"] >= 0.65] if "churn_probability" in df.columns else pd.DataFrame()
    at_risk_count = len(at_risk_df)
    at_risk_rev = float(at_risk_df["total_spend"].sum()) if not at_risk_df.empty and "total_spend" in at_risk_df.columns else 0.0

    insights: List[Dict[str, Any]] = []

    # 1. Revenue Concentration (Pareto Distribution)
    if "total_spend" in df.columns and total_gmv > 0:
        p80_spend = float(df["total_spend"].quantile(0.80))
        top_20_rev = float(df[df["total_spend"] >= p80_spend]["total_spend"].sum())
        top_20_share = top_20_rev / max(1.0, total_gmv)

        if "rfm_segment" in df.columns:
            seg_spend = df.groupby("rfm_segment")["total_spend"].sum()
            top_seg_name = str(seg_spend.idxmax())
            top_seg_revenue = float(seg_spend.max())
            top_seg_share = top_seg_revenue / max(1.0, total_gmv)
            evidence_pareto = (
                f"The top 20% of spenders account for {format_pct(top_20_share)} ({format_brl(top_20_rev)}) "
                f"of total GMV. Leading segment '{top_seg_name}' contributes {format_brl(top_seg_revenue)} ({format_pct(top_seg_share)})."
            )
        else:
            evidence_pareto = (
                f"The top 20% of spenders account for {format_pct(top_20_share)} ({format_brl(top_20_rev)}) of total GMV."
            )

        insights.append({
            "title": "Revenue Concentration (Pareto Distribution)",
            "observation": "A small minority of top spenders accounts for the disproportionate share of cumulative merchandise sales.",
            "evidence": evidence_pareto,
            "implication": "Prioritize VIP retention and loyalty perks for this cohort to safeguard the core revenue foundation.",
            "badge": "Pareto Health",
            "kind": "info",
        })

    # 2. Regional Demand Hubs (Geographic Focus)
    if "state" in df.columns and total_gmv > 0:
        state_spend = df.groupby("state")["total_spend"].sum()
        top_state = str(state_spend.idxmax())
        top_state_revenue = float(state_spend.max())
        top_state_share = top_state_revenue / max(1.0, total_gmv)

        insights.append({
            "title": "Regional Demand Hubs (Geographic Focus)",
            "observation": "Merchandise demand is strongly clustered in key economic centers.",
            "evidence": f"State '{top_state}' represents the largest geographic market with {format_brl(top_state_revenue)} ({format_pct(top_state_share)} of total GMV).",
            "implication": "Optimize regional fulfillment, carrier routing, and localized promotional campaigns in primary states.",
            "badge": "Geographic Intelligence",
            "kind": "success",
        })

    # 3. Single-Purchase Drop-Off Opportunity (Retention Lever)
    insights.append({
        "title": "Single-Purchase Drop-Off Opportunity",
        "observation": "The majority of customer relationships conclude after a single completed purchase.",
        "evidence": f"Repeat buyer rate is {format_pct(repeat_rate)} ({repeat_customers:,} multi-order buyers out of {total_customers:,} total profiles).",
        "implication": "Deploying an automated 14-day post-purchase replenishment workflow represents the highest leverage CLV multiplier.",
        "badge": "Retention Lever",
        "kind": "warning" if repeat_rate < 0.10 else "info",
    })

    # 4. Churn Risk Exposure & Capital Protection (Risk Exposure)
    insights.append({
        "title": "Churn Risk Exposure & Capital Protection",
        "observation": "A substantial amount of historical revenue belongs to customers currently exhibiting extended inactivity.",
        "evidence": f"{at_risk_count:,} customers ({format_pct(at_risk_count / max(1, total_customers))}) represent {format_brl(at_risk_rev)} in cumulative merchandise spend at risk (churn probability >= 65%).",
        "implication": "Deploy targeted win-back incentives to reactivate lapsed relationships before complete account attrition.",
        "badge": "Risk Exposure",
        "kind": "alert",
    })

    return insights
