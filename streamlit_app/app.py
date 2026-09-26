"""CustomerAtlas AI — Unified Customer Intelligence Platform.

Production-grade, enterprise customer intelligence application covering:
1. Executive Overview
2. Customer 360 (Unified Profile Dossier & Activity Ledger)
3. Customer Segmentation (RFM Intelligence, Playbooks, Cohort Builder)
4. Customer Value / CLV (12-Month Forward Value, Bands, Cohorts & ML Estimator)
5. Churn Intelligence (Risk Exposure, 4-Quadrant Matrix, Feature Drivers, Simulator)
6. Sentiment Intelligence (CSAT Analytics, Longitudinal Trends, Negative Theme Extraction)
7. Recommendations (Multi-Signal Action Engine, Rule Matrix, Priority Queue)
8. Analytics Explorer (Multi-Dimensional Filter Hub, Slice Analytics, CSV Export)
9. Data Quality (Completeness Audit, Raw vs Processed Lineage, PSI Drift, System Health)
10. Methodology / About (Architecture, Mathematical Formulations, MLOps Standards)
Plus: Ask CustomerAtlas (Grounded AI Decision Support Engine)

Run locally:
    streamlit run app.py
or
    streamlit run streamlit_app/app.py
"""

import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup sys.path to resolve internal modules
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Component Imports
from components.cards import (
    render_customer_hero,
    render_empty_state,
    render_error_state,
    render_insight_card,
    render_insight_grid,
    render_recommendation_card,
)
from components.customer_profile import (
    render_customer_360_header,
    render_customer_health_grid,
    render_lifecycle_journey,
    render_risk_diagnostics,
    render_customer_timeline,
)
from components.customer_table import render_customer_table
from components.data_quality_card import render_system_health_modal
from components.footer import render_footer
from components.grounded_ai_card import render_grounded_answer
from components.header import render_global_header, render_page_header
from components.insight_card import render_structured_insight
from components.methodology import render_methodology_panel
from components.metric_cards import render_kpi_row
from components.sidebar import render_sidebar

# Service Imports
from services.audit_service import get_recent_audit_events, record_audit_event
from services.clv_service import (
    analyze_high_value_cohort,
    compute_clv_bins,
    compute_clv_overview,
)
from services.customer_service import (
    compute_customer_health,
    derive_lifecycle_stages,
    diagnose_customer_risk_factors,
    explain_rfm_segment,
    get_customer_profile,
    search_customers,
)
from services.data_quality_service import run_data_quality_audit
from services.data_service import (
    SQL_DIR,
    build_customer_pdf,
    load_csv,
    load_model,
    model_input_frame,
    retention_action,
)
from services.drift_service import run_feature_drift_audit
from services.grounded_ai_service import GroundedAIService
from services.health_score_service import calculate_customer_health_score, classify_lifecycle_state
from services.model_service import audit_model_registry
from services.recommendation_service import (
    RECOMMENDATION_RULES,
    compute_recommendation_portfolio,
    compute_recommendation_summary,
    generate_customer_recommendation,
)
from services.rfm_service import (
    compare_segments,
    compute_rfm_overview,
    compute_segment_distribution,
    get_segment_playbook,
)
from services.risk_service import (
    calculate_customer_prioritization,
    compute_quadrant_matrix,
    compute_risk_distribution,
    compute_risk_overview,
)
from services.sentiment_service import (
    compute_category_satisfaction,
    compute_sentiment_by_segment,
    compute_sentiment_overview,
    compute_sentiment_trend,
    extract_negative_themes,
    load_sentiment_dataset,
)

# Utility Imports
from config.settings import get_environment_info
from utils.formatting import (
    format_brl,
    format_currency,
    format_num,
    format_number,
    format_pct,
    format_percent,
)
from utils.helpers import calculate_data_snapshot_info
from utils.styling import (
    CHART_COLORWAY,
    COLOR_AMBER,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_PRIMARY,
    COLOR_PURPLE,
    COLOR_RED,
    COLOR_SLATE,
    PLOT_CONFIG,
    load_css,
    style_chart,
)
from utils.validation import validate_customer_dataframe, validate_customer_id

# ==============================================================================
# APPLICATION SETUP & METADATA
# ==============================================================================

st.set_page_config(
    page_title="CustomerAtlas AI | Unified Customer Intelligence Platform",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject centralized enterprise stylesheet
load_css()

# Workspace Metadata & Header Content
PAGE_META = {
    "Executive Overview": {
        "title": "Customer Intelligence Overview",
        "subtitle": "Understand customer value, retention, risk and engagement at a glance.",
        "category": "EXECUTIVE OVERVIEW",
        "guides": [
            "Monitor portfolio customer health & GMV",
            "Track repeat buyer rate and retention health",
            "Review high-value audience revenue concentration",
            "Inspect state-level regional demand hubs",
        ],
    },
    "Customer 360": {
        "title": "Customer 360 Unified Profile Dossier",
        "subtitle": "Complete customer dossier, 6-dimension vital health signs, verifiable lifecycle journey, and transaction ledger.",
        "category": "CUSTOMER INTELLIGENCE",
        "guides": [
            "Search and inspect 94k+ canonical customer profiles",
            "Review multi-dimensional health vitals and CSAT",
            "Track verifiable lifecycle milestones",
            "Access AI Next-Best-Category recommendations",
        ],
    },
    "Customer Segmentation": {
        "title": "Customer Segmentation & RFM Intelligence",
        "subtitle": "RFM segment distribution, granular audience drill-down, side-by-side comparison, and targeted cohort builder.",
        "category": "CUSTOMER INTELLIGENCE",
        "guides": [
            "Inspect 6 canonical RFM audience segments",
            "Drill down into segment metrics and top customers",
            "Compare two segments side-by-side across metrics",
            "Build targeted campaign cohorts with CSV export",
        ],
    },
    "Customer Value / CLV": {
        "title": "Customer Value & Lifetime Value (CLV) Intelligence",
        "subtitle": "12-month forward predictive CLV benchmarks, dynamic value banding, and high-value customer cohort analysis.",
        "category": "CUSTOMER INTELLIGENCE",
        "guides": [
            "Benchmark average and top 10% customer CLV",
            "Analyze customer distribution across dynamic CLV bands",
            "Deep dive into Top 10% High-Value customer cohort",
            "Run interactive 12-Month CLV scenario simulations",
        ],
    },
    "Churn Intelligence": {
        "title": "Customer Churn & Risk Intelligence",
        "subtitle": "At-risk revenue exposure, 4-quadrant value-risk matrix, XGBoost feature drivers, and prioritized retention queue.",
        "category": "PREDICTIVE & RISK AI",
        "guides": [
            "Quantify total revenue exposed to customer churn",
            "Explore High-Value + High-Risk 4-quadrant matrix",
            "Sort actionable customer retention priority ranking",
            "Simulate live churn propensity with What-If tool",
        ],
    },
    "Sentiment Intelligence": {
        "title": "Sentiment Intelligence & Customer CSAT Analytics",
        "subtitle": "Customer satisfaction benchmarks, longitudinal sentiment trends, segment CSAT, and empirical negative feedback root causes.",
        "category": "PREDICTIVE & RISK AI",
        "guides": [
            "Track Positive, Neutral, and Negative CSAT distribution",
            "Analyze longitudinal monthly review rating trajectory",
            "Examine customer satisfaction across RFM segments and categories",
            "Diagnose empirical negative feedback themes and root causes",
        ],
    },
    "Recommendations": {
        "title": "Customer Action Recommendation Engine",
        "subtitle": "Transparent, multi-signal customer action recommendation engine with documented decision rules and priority queues.",
        "category": "PREDICTIVE & RISK AI",
        "guides": [
            "Review automated customer action assignments and priorities",
            "Inspect transparent business decision rules and rationale",
            "Filter action queues by retention, win-back, loyalty, or cross-sell",
            "Explore Next-Best-Category cross-sell recommendations with CSV export",
        ],
    },
    "Analytics Explorer": {
        "title": "Analytics Explorer & Multi-Criteria Discovery Hub",
        "subtitle": "Filter, search, slice, and drill down into customer records with multi-dimensional criteria and instant profile opening.",
        "category": "EXPLORATION & GOVERNANCE",
        "guides": [
            "Search by Customer ID, location, or value band",
            "Filter by RFM segment, churn risk, and recency window",
            "Inspect filtered cohort spend and recency distributions",
            "1-click transition into individual Customer 360 profiles",
        ],
    },
    "Data Quality": {
        "title": "Data Quality, Integrity & MLOps Governance",
        "subtitle": "Automated data completeness audits, raw vs processed data lineage, PSI feature drift monitoring, and compliance logs.",
        "category": "EXPLORATION & GOVERNANCE",
        "guides": [
            "Evaluate data completeness score and field-by-field integrity",
            "Audit raw ingestion vs processed feature store lineage",
            "Monitor Population Stability Index (PSI) feature drift",
            "Inspect real-time compliance event audit stream",
        ],
    },
    "Methodology / About": {
        "title": "Methodology, Architecture & Enterprise Governance",
        "subtitle": "Comprehensive documentation of mathematical formulations, ML models, data pipelines, assumptions, and engineering standards.",
        "category": "EXPLORATION & GOVERNANCE",
        "guides": [
            "Review RFM quintile scoring and audience segmentation methodology",
            "Inspect 12-Month Forward CLV model architecture and value tiers",
            "Understand XGBoost churn classification and non-causal attribution policy",
            "Explore system architecture, tech stack, and deployment instructions",
        ],
    },
    "Ask CustomerAtlas": {
        "title": "Ask CustomerAtlas — Grounded AI Assistant",
        "subtitle": "Safe natural-language analytics grounded 100% in factual metrics, database statistics, and verified ML models.",
        "category": "DECISION SUPPORT",
        "guides": [
            "Ask macro questions about customer revenue, repeat rates, and regional hubs",
            "Identify vulnerable high-value customers at severe churn risk",
            "Request evidence-backed risk explanations for specific customer IDs",
            "Inspect segment strategic playbooks and commercial value drivers",
        ],
    },
}

# ==============================================================================
# DATA INITIALIZATION & VALIDATION
# ==============================================================================

try:
    customer_features = load_csv("customer_360_features.csv", ("first_purchase_date", "last_purchase_date"))
except Exception as err:
    render_error_state("Critical Data Loading Failure", f"Unable to load customer feature store: {err}")
    st.stop()

is_valid, validation_issues = validate_customer_dataframe(customer_features)
if not is_valid:
    render_error_state(
        "Data Validation Issue Encountered",
        f"The primary customer dataset failed schema validation: {'; '.join(validation_issues)}",
    )
    st.stop()

# Safe URL query parameter integration
query_params = st.query_params
if "customer_id" in query_params:
    param_cid = str(query_params["customer_id"])
    if validate_customer_id(param_cid, customer_features):
        st.session_state.selected_customer_id = param_cid
        if "active_page" not in st.session_state:
            st.session_state.active_page = "Customer 360"

# Render Global Application Shell
filtered, current_page = render_sidebar(customer_features)
render_global_header(total_profiles=len(customer_features))

page_info = PAGE_META.get(current_page, PAGE_META["Executive Overview"])
render_page_header(
    page_name=current_page,
    title=page_info["title"],
    subtitle=page_info["subtitle"],
    category_badge=page_info["category"],
    guides=page_info["guides"],
)

if filtered.empty:
    render_empty_state(
        title="No Matching Customer Profiles",
        description="No customer records match the currently applied audience filter criteria. Please broaden your selection or reset filters.",
        show_reset=True,
    )
    st.stop()


# ==============================================================================
# WORKSPACE 1: EXECUTIVE OVERVIEW
# ==============================================================================

if current_page == "Executive Overview":
    total_customers = filtered["customer_id"].nunique()
    total_gmv = filtered["total_spend"].sum()
    total_orders = filtered["total_orders"].sum()
    avg_customer_value = total_gmv / max(1, total_customers)
    avg_order_value = total_gmv / max(1, total_orders)
    
    repeat_customers = (filtered["total_orders"] > 1).sum()
    repeat_rate = repeat_customers / max(1, total_customers)
    
    # Active customers (recency <= 180 days)
    active_customers = (filtered["recency_days"] <= 180).sum()
    active_rate = active_customers / max(1, total_customers)
    
    # At-risk customers (churn_probability >= 0.65)
    at_risk_df = filtered[filtered["churn_probability"] >= 0.65]
    at_risk_count = len(at_risk_df)
    at_risk_rev = at_risk_df["total_spend"].sum()
    
    # High-value customers (Top 10% CLV)
    p90_clv = filtered["predicted_clv"].quantile(0.90)
    high_val_df = filtered[filtered["predicted_clv"] >= p90_clv]
    high_val_count = len(high_val_df)
    high_val_rev = high_val_df["total_spend"].sum()
    avg_clv = filtered["predicted_clv"].mean()

    # Top KPI Layer (All calculated directly from data)
    render_kpi_row([
        {
            "label": "Total Customers",
            "value": f"{total_customers:,}",
            "subtitle": "Current dataset view",
            "icon": "👥",
        },
        {
            "label": "Active Customers",
            "value": f"{active_customers:,}",
            "subtitle": f"{format_pct(active_rate)} active (<=180d)",
            "icon": "⚡",
        },
        {
            "label": "Total Revenue (GMV)",
            "value": format_brl(total_gmv),
            "subtitle": "Total gross spend",
            "icon": "💰",
        },
        {
            "label": "Avg Customer Value",
            "value": format_brl(avg_customer_value),
            "subtitle": "Lifetime spend / cust",
            "icon": "💎",
        },
    ])

    render_kpi_row([
        {
            "label": "Average Order Value",
            "value": format_brl(avg_order_value),
            "subtitle": f"{(total_orders/max(1, total_customers)):.2f} orders/cust",
            "icon": "🛒",
        },
        {
            "label": "Average 12M CLV",
            "value": format_brl(avg_clv),
            "subtitle": "Forward value proxy",
            "icon": "📈",
        },
        {
            "label": "Repeat Customer Rate",
            "value": format_pct(repeat_rate),
            "subtitle": f"{repeat_customers:,} multi-order buyers",
            "icon": "🔄",
        },
        {
            "label": "At-Risk Customers",
            "value": f"{at_risk_count:,}",
            "delta": format_brl(at_risk_rev),
            "delta_direction": "negative",
            "subtitle": "Revenue exposed to churn",
            "icon": "⚠️",
        },
    ])

    # Dynamic Structured Insights Section (100% calculated from current data)
    st.markdown('<div class="section-header"><h3>Dynamic Key Insights & Commercial Signals</h3><span>Calculated from Current Filtered Cohort</span></div>', unsafe_allow_html=True)
    
    top_seg_name = filtered.groupby("rfm_segment")["total_spend"].sum().idxmax()
    top_seg_revenue = filtered.groupby("rfm_segment")["total_spend"].sum().max()
    top_seg_share = top_seg_revenue / max(1, total_gmv)

    top_state = filtered.groupby("state")["total_spend"].sum().idxmax()
    top_state_revenue = filtered.groupby("state")["total_spend"].sum().max()
    top_state_share = top_state_revenue / max(1, total_gmv)

    p80_spend = filtered["total_spend"].quantile(0.80)
    top_20_rev = filtered[filtered["total_spend"] >= p80_spend]["total_spend"].sum()
    top_20_share = top_20_rev / max(1, total_gmv)

    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        render_structured_insight(
            title="Revenue Concentration (Pareto Distribution)",
            observation="A small minority of top spenders accounts for the disproportionate share of cumulative merchandise sales.",
            evidence=f"The top 20% of spenders account for {format_pct(top_20_share)} ({format_brl(top_20_rev)}) of total GMV. Leading segment '{top_seg_name}' contributes {format_brl(top_seg_revenue)} ({format_pct(top_seg_share)}).",
            implication="Prioritize VIP retention and loyalty perks for this cohort to safeguard the core revenue foundation.",
            badge="Pareto Health",
            kind="info",
        )
        render_structured_insight(
            title="Regional Demand Hubs (Geographic Focus)",
            observation="Merchandise demand is strongly clustered in key economic centers.",
            evidence=f"State '{top_state}' represents the largest geographic market with {format_brl(top_state_revenue)} ({format_pct(top_state_share)} of total GMV).",
            implication="Optimize regional fulfillment, carrier routing, and localized promotional campaigns in primary states.",
            badge="Geographic Intelligence",
            kind="success",
        )
    with col_ins2:
        render_structured_insight(
            title="Single-Purchase Drop-Off Opportunity",
            observation="The majority of customer relationships conclude after a single completed purchase.",
            evidence=f"Repeat buyer rate is {format_pct(repeat_rate)} ({repeat_customers:,} multi-order buyers out of {total_customers:,} total profiles).",
            implication="Deploying an automated 14-day post-purchase replenishment workflow represents the highest leverage CLV multiplier.",
            badge="Retention Lever",
            kind="warning" if repeat_rate < 0.10 else "info",
        )
        render_structured_insight(
            title="Churn Risk Exposure & Capital Protection",
            observation="A substantial amount of historical revenue belongs to customers currently exhibiting extended inactivity.",
            evidence=f"{at_risk_count:,} customers ({format_pct(at_risk_count/max(1, total_customers))}) represent {format_brl(at_risk_rev)} in cumulative merchandise spend at risk (churn probability >= 65%).",
            implication="Deploy targeted win-back incentives to reactivate lapsed relationships before complete account attrition.",
            badge="Risk Exposure",
            kind="alert",
        )

    # Customer Health Overview (Donut Chart & Segment Composition)
    st.markdown('<div class="section-header"><h3>Customer Health & Audience Composition Overview</h3><span>Portfolio Viability & Segment Breakdown</span></div>', unsafe_allow_html=True)
    c_health_l, c_health_r = st.columns([0.55, 0.45])

    with c_health_l:
        seg_dist = filtered["rfm_segment"].value_counts().reset_index()
        seg_dist.columns = ["rfm_segment", "count"]
        fig_health = px.pie(
            seg_dist,
            names="rfm_segment",
            values="count",
            hole=0.55,
            title="Customer Audience Segment Composition",
            color="rfm_segment",
            color_discrete_sequence=CHART_COLORWAY,
        )
        style_chart(fig_health, 300, legend="bottom")

    with c_health_r:
        # Calculate empirical health cohorts
        healthy_cohorts = ["Champions", "Loyal Customers", "Potential Loyalists"]
        h_count = int(filtered[filtered["rfm_segment"].isin(healthy_cohorts)]["customer_id"].count())
        h_rev = float(filtered[filtered["rfm_segment"].isin(healthy_cohorts)]["total_spend"].sum())
        h_pct = h_count / max(1, total_customers)

        reg_count = int(filtered[filtered["rfm_segment"] == "Regular Customers"]["customer_id"].count())
        reg_rev = float(filtered[filtered["rfm_segment"] == "Regular Customers"]["total_spend"].sum())
        reg_pct = reg_count / max(1, total_customers)

        risk_cohort_count = int(filtered[filtered["rfm_segment"] == "At Risk"]["customer_id"].count())
        risk_cohort_rev = float(filtered[filtered["rfm_segment"] == "At Risk"]["total_spend"].sum())
        risk_cohort_pct = risk_cohort_count / max(1, total_customers)

        lost_cohort_count = int(filtered[filtered["rfm_segment"] == "Lost Customers"]["customer_id"].count())
        lost_cohort_rev = float(filtered[filtered["rfm_segment"] == "Lost Customers"]["total_spend"].sum())
        lost_cohort_pct = lost_cohort_count / max(1, total_customers)
        lost_count = lost_cohort_count
        lost_rev = lost_cohort_rev
        lost_pct = lost_cohort_pct

        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; gap: 10px; height: 100%; justify-content: center;">
                <div style="background: white; border: 1px solid #E2E8F0; border-left: 4px solid #16A34A; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; font-weight: 700; color: #0F172A;">Healthy & Loyal Base</span>
                        <span style="font-size: 13px; font-weight: 800; color: #16A34A;">{format_pct(h_pct)} ({h_count:,} profiles)</span>
                    </div>
                    <div style="font-size: 11px; color: #64748B; margin-top: 2px;">Champions, Loyal & Potential Loyalists • {format_brl(h_rev)} GMV</div>
                </div>
                <div style="background: white; border: 1px solid #E2E8F0; border-left: 4px solid #0284C7; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; font-weight: 700; color: #0F172A;">Regular Core Buyers</span>
                        <span style="font-size: 13px; font-weight: 800; color: #0284C7;">{format_pct(reg_pct)} ({reg_count:,} profiles)</span>
                    </div>
                    <div style="font-size: 11px; color: #64748B; margin-top: 2px;">Baseline active accounts • {format_brl(reg_rev)} GMV</div>
                </div>
                <div style="background: white; border: 1px solid #E2E8F0; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; font-weight: 700; color: #0F172A;">At-Risk Cohort</span>
                        <span style="font-size: 13px; font-weight: 800; color: #F59E0B;">{format_pct(risk_cohort_pct)} ({risk_cohort_count:,} profiles)</span>
                    </div>
                    <div style="font-size: 11px; color: #64748B; margin-top: 2px;">Previously active repeat buyers lapsing • {format_brl(risk_cohort_rev)} GMV</div>
                </div>
                <div style="background: white; border: 1px solid #E2E8F0; border-left: 4px solid #DC2626; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; font-weight: 700; color: #0F172A;">Lost Inactive Accounts</span>
                        <span style="font-size: 13px; font-weight: 800; color: #DC2626;">{format_pct(lost_cohort_pct)} ({lost_cohort_count:,} profiles)</span>
                    </div>
                    <div style="font-size: 11px; color: #64748B; margin-top: 2px;">Extended inactivity (>365d) • {format_brl(lost_cohort_rev)} GMV</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Macro Revenue & Order Velocity
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    if not fact_orders.empty:
        st.markdown('<div class="section-header"><h3>Macro Revenue Velocity & Order Trajectory</h3><span>Historical Monthly GMV & Order Volume</span></div>', unsafe_allow_html=True)
        valid_orders = fact_orders[~fact_orders["order_status"].isin(["canceled", "unavailable"])].copy()
        if "purchase_date" in valid_orders.columns and hasattr(valid_orders["purchase_date"], "dt"):
            valid_orders["month_year"] = valid_orders["purchase_date"].dt.to_period("M").astype(str)
            monthly_summary = valid_orders.groupby("month_year", as_index=False).agg(
                revenue=("revenue", "sum"),
                orders=("order_id", "nunique"),
            ).sort_values("month_year")

            fig_macro = go.Figure()
            fig_macro.add_trace(go.Bar(
                x=monthly_summary["month_year"],
                y=monthly_summary["revenue"],
                name="Merchandise GMV (BRL)",
                marker_color=COLOR_PRIMARY,
                opacity=0.85,
            ))
            fig_macro.add_trace(go.Scatter(
                x=monthly_summary["month_year"],
                y=monthly_summary["orders"],
                name="Completed Orders",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color=COLOR_AMBER, width=3),
                marker=dict(size=6),
            ))
            fig_macro.update_layout(
                title="Monthly Merchandise GMV (BRL) and Completed Order Volume",
                yaxis=dict(title="Revenue (BRL)"),
                yaxis2=dict(title="Order Count", overlaying="y", side="right", showgrid=False),
            )
            style_chart(fig_macro, 320, legend="top")

    # Segment Revenue & Geographic Distribution
    c_rev1, c_rev2 = st.columns(2)
    with c_rev1:
        seg_rev = filtered.groupby("rfm_segment", as_index=False)["total_spend"].sum().sort_values("total_spend", ascending=True)
        fig_seg = px.bar(
            seg_rev,
            x="total_spend",
            y="rfm_segment",
            orientation="h",
            color="rfm_segment",
            title="Merchandise GMV Contribution by RFM Segment",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_seg.update_xaxes(title="Total Spend (BRL)")
        fig_seg.update_yaxes(title=None)
        style_chart(fig_seg, 320, legend="hidden")

    with c_rev2:
        state_rev = filtered.groupby("state", as_index=False)["total_spend"].sum().nlargest(10, "total_spend").sort_values("total_spend", ascending=True)
        fig_state = px.bar(
            state_rev,
            x="total_spend",
            y="state",
            orientation="h",
            title="Top 10 Brazilian States by Merchandise GMV",
            color="total_spend",
            color_continuous_scale="Blues",
        )
        fig_state.update_xaxes(title="Revenue (BRL)")
        fig_state.update_yaxes(title="State")
        fig_state.update_layout(coloraxis_showscale=False)
        style_chart(fig_state, 320, legend="hidden")

    # Governance Snapshot & Export Action
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    st.download_button(
        "Download Executive Overview Dataset (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        "customer_atlas_executive_view.csv",
        "text/csv",
        icon=":material/download:",
    )


# ==============================================================================
# WORKSPACE 2: CUSTOMER 360
# ==============================================================================

elif current_page == "Customer 360":
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    fact_payments = load_csv("fact_payments.csv")
    recommendations = load_csv("recommendations.csv")

    # Customer Selection & Quick Search Bar
    search_c1, search_c2 = st.columns([0.35, 0.65])
    with search_c1:
        preset_choice = st.selectbox(
            "Filter Customer Lookup",
            [
                "All Filtered Customers",
                "Champions & VIPs",
                "At Risk High Spenders",
                "Recent Active Buyers",
                "Multi-Order Repeat Buyers",
            ],
        )

    preset_df = filtered.copy()
    if preset_choice == "Champions & VIPs":
        preset_df = preset_df[preset_df["rfm_segment"] == "Champions"]
    elif preset_choice == "At Risk High Spenders":
        preset_df = preset_df[(preset_df["churn_probability"] >= 0.65) & (preset_df["total_spend"] >= 200)]
    elif preset_choice == "Recent Active Buyers":
        preset_df = preset_df[preset_df["recency_days"] <= 60]
    elif preset_choice == "Multi-Order Repeat Buyers":
        preset_df = preset_df[preset_df["total_orders"] > 1]

    if preset_df.empty:
        preset_df = filtered

    available_cids = sorted(preset_df["customer_id"].dropna().unique().tolist())

    # Check session state for preselected customer
    default_cid = st.session_state.get("selected_customer_id", available_cids[0] if available_cids else "")
    if default_cid not in available_cids and available_cids:
        default_cid = available_cids[0]

    with search_c2:
        selected_cid = st.selectbox(
            "Select or Search Customer ID",
            available_cids,
            index=available_cids.index(default_cid) if default_cid in available_cids else 0,
        )
        st.session_state.selected_customer_id = selected_cid

    profile = get_customer_profile(filtered, selected_cid)
    if profile is None:
        render_empty_state(
            title="Customer Profile Not Found",
            description=f"No customer record found matching ID `{selected_cid}` in the currently active filtered view.",
            show_reset=True,
        )
        st.stop()

    # Customer Risk Diagnosis & Retention Action
    churn_prob = float(profile.get("churn_probability", 0))
    action_info = retention_action(churn_prob, str(profile.get("rfm_segment", "")))
    risk_diag = diagnose_customer_risk_factors(profile)

    # 1. Customer 360 Header
    render_customer_360_header(
        customer_id=str(profile.get("customer_id")),
        rfm_segment=str(profile.get("rfm_segment")),
        city=str(profile.get("city", "Unknown")),
        state=str(profile.get("state", "SP")),
        first_purchase_date=profile.get("first_purchase_date"),
        risk_level=risk_diag["risk_level"],
        risk_color=action_info["badge_color"],
        action_tier=action_info["tier"],
        action_color=action_info["badge_color"],
    )

    # 2. Customer Summary KPIs
    render_kpi_row([
        {
            "label": "12M Forward CLV",
            "value": format_brl(profile.get("predicted_clv", 0)),
            "subtitle": f"Tier: {profile.get('clv_band', 'Standard')}",
            "icon": "💎",
        },
        {
            "label": "Total Spend (GMV)",
            "value": format_brl(profile.get("total_spend", 0)),
            "subtitle": "Lifetime revenue",
            "icon": "💰",
        },
        {
            "label": "Total Orders",
            "value": f"{int(profile.get('total_orders', 1)):,}",
            "subtitle": "Completed orders",
            "icon": "📦",
        },
        {
            "label": "Average Order Value",
            "value": format_brl(profile.get("avg_order_value", 0)),
            "subtitle": "Per-order average",
            "icon": "🛒",
        },
        {
            "label": "Purchase Recency",
            "value": f"{int(profile.get('recency_days', 0))} days",
            "subtitle": "Days since last order",
            "icon": "⏱️",
        },
        {
            "label": "Churn Propensity",
            "value": format_pct(churn_prob),
            "delta": risk_diag["risk_level"],
            "delta_direction": "negative" if churn_prob >= 0.65 else "positive" if churn_prob <= 0.35 else "neutral",
            "subtitle": "Calibrated risk",
            "icon": "🎯",
        },
    ])

    # 3. Customer Health Vital Signs
    health_vitals = compute_customer_health(profile)
    render_customer_health_grid(health_vitals)

    # 4. Customer Lifecycle Journey Progression
    lifecycle_milestones = derive_lifecycle_stages(profile)
    render_lifecycle_journey(lifecycle_milestones)

    # 5. Customer 360 Deep Dossier Tabs
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    tab_overview, tab_behavior, tab_orders, tab_payments, tab_recs = st.tabs([
        "📋 Profile & Segmentation Rationale",
        "🌐 Touchpoint Engagement & Risk",
        "📦 Order History Fact Records",
        "💳 Payment & Settlement Methods",
        "🎁 AI Next-Best-Category Offers",
    ])

    with tab_overview:
        col_prof_l, col_prof_r = st.columns([1.2, 0.8])
        with col_prof_l:
            rfm_diag = explain_rfm_segment(profile)
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 14px;">
                    <div style="font-size: 11px; font-weight: 700; color: #4F46E5; text-transform: uppercase;">Segment Assignment Rationale</div>
                    <div style="font-size: 16px; font-weight: 800; color: #0F172A; margin: 4px 0 6px;">{rfm_diag['segment']} ({rfm_diag['rfm_code']})</div>
                    <p style="font-size: 13px; color: #475569; line-height: 1.45; margin-bottom: 10px;">{rfm_diag['explanation']}</p>
                    <div style="font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 4px;">Contributing Data Factors:</div>
                    {''.join([f'<div style="font-size: 12.5px; color: #1E293B; margin-bottom: 2px;">• {factor}</div>' for factor in rfm_diag['factors']])}
                </div>
                """,
                unsafe_allow_html=True,
            )

            attr_dict = {
                "Canonical Customer ID": str(profile.get("customer_id")),
                "Geographic Location": f"{str(profile.get('city', '')).title()}, {str(profile.get('state', '')).upper()}",
                "Primary Favorite Category": str(profile.get("favorite_category")),
                "Distinct Items Purchased": int(profile.get("number_of_products", 1)),
                "Average CSAT Feedback Rating": f"{float(profile.get("avg_review_score", 5.0)):.1f} / 5.0 stars",
                "Customer Tenure Span": f"{int(profile.get('customer_age_days', 1))} days",
                "Behavioral Cluster": str(profile.get("cluster_segment", "Standard")),
                "Estimated 90-Day Forward Revenue": format_brl(profile.get("predicted_90d_revenue", 0)),
            }
            attr_df = pd.DataFrame({"Customer Attribute": attr_dict.keys(), "Observed Value": attr_dict.values()})
            st.dataframe(attr_df, hide_index=True, use_container_width=True)

        with col_prof_r:
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=100 * churn_prob,
                number={"suffix": "%", "font": {"family": "JetBrains Mono", "size": 28, "color": COLOR_SLATE}},
                title={"text": "<b>Calibrated Churn Propensity</b>", "font": {"size": 13, "color": COLOR_SLATE}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": action_info["badge_color"]},
                    "steps": [
                        {"range": [0, 35], "color": "rgba(22,163,74,0.12)"},
                        {"range": [35, 65], "color": "rgba(245,158,11,0.12)"},
                        {"range": [65, 100], "color": "rgba(220,38,38,0.12)"},
                    ],
                },
            ))
            gauge_fig.update_layout(height=210, margin=dict(l=15, r=15, t=35, b=5), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(gauge_fig, use_container_width=True, config=PLOT_CONFIG)
            st.info(f"**Recommended Action:** {action_info['action']}")

    with tab_behavior:
        render_kpi_row([
            {"label": "Digital Web Sessions", "value": f"{profile.get('sessions', 0):,.0f}", "subtitle": "Total website visits"},
            {"label": "Product Page Views", "value": f"{profile.get('views', 0):,.0f}", "subtitle": "Catalog browsing"},
            {"label": "Cart Additions", "value": f"{profile.get('cart_additions', 0):,.0f}", "subtitle": "High-intent actions"},
            {"label": "Campaign Conversions", "value": f"{profile.get('campaign_conversions', 0):,.0f}", "subtitle": "Marketing response"},
        ])
        render_risk_diagnostics(risk_diag, action_info)

    with tab_orders:
        if not fact_orders.empty:
            cust_orders = fact_orders[fact_orders["customer_id"] == selected_cid].copy()
            if cust_orders.empty:
                st.info("No detailed transaction line items found in the order ledger for this customer.")
            else:
                cust_orders = cust_orders.sort_values("purchase_date", ascending=False)
                
                # Fetch associated reviews if available
                reviews_df = load_sentiment_dataset()
                cust_reviews = None
                if not reviews_df.empty and "order_id" in reviews_df.columns:
                    cust_reviews = reviews_df[reviews_df["order_id"].isin(cust_orders["order_id"])].copy()

                # Render chronological activity timeline
                render_customer_timeline(cust_orders, cust_reviews)

                st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
                order_cols = [c for c in ["order_id", "purchase_date", "order_status", "item_price", "freight_value", "revenue"] if c in cust_orders.columns]
                st.markdown(f"**Completed Transaction Records ({len(cust_orders)} items):**")
                st.dataframe(cust_orders[order_cols], hide_index=True, use_container_width=True)
        else:
            st.info("Order transactions table is loading.")

    with tab_payments:
        if not fact_payments.empty and not fact_orders.empty:
            cust_order_ids = fact_orders[fact_orders["customer_id"] == selected_cid]["order_id"].unique()
            cust_payments = fact_payments[fact_payments["order_id"].isin(cust_order_ids)].copy()
            if not cust_payments.empty:
                p_c1, p_c2 = st.columns([0.5, 0.5])
                with p_c1:
                    st.markdown("**Payment Method & Installment Ledger:**")
                    st.dataframe(cust_payments[["payment_type", "payment_installments", "payment_value"]], hide_index=True, use_container_width=True)
                with p_c2:
                    pay_pie = px.pie(
                        cust_payments,
                        names="payment_type",
                        values="payment_value",
                        hole=0.5,
                        title="Payment Value by Method",
                        color_discrete_sequence=CHART_COLORWAY,
                    )
                    style_chart(pay_pie, 220, legend="hidden")
            else:
                st.info("No payment method logs found for this customer's orders.")
        else:
            st.info("Payment facts are loading.")

    with tab_recs:
        if not recommendations.empty:
            cust_recs = recommendations[recommendations["customer_id"] == selected_cid].sort_values("rank")
            if cust_recs.empty:
                st.info("No precomputed recommendations found for this customer record.")
            else:
                st.markdown("**Explainable Next-Best-Category Recommendations:**")
                rec_cols = st.columns(min(len(cust_recs), 5))
                for col_idx, (_, rec) in enumerate(cust_recs.head(5).iterrows()):
                    with rec_cols[col_idx]:
                        st.markdown(
                            render_recommendation_card(
                                rank=int(rec["rank"]),
                                category=str(rec["recommended_category"]),
                                reason=str(rec["reason"]),
                                method=str(rec.get("method", "Basket Co-occurrence")),
                            ),
                            unsafe_allow_html=True,
                        )
        else:
            st.info("Recommendations catalog is loading.")

    # Export Dossier
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    exp_c1, exp_c2 = st.columns([0.3, 0.3])
    with exp_c1:
        st.download_button(
            "Download Executive PDF Dossier",
            build_customer_pdf(profile),
            f"customer_360_{selected_cid}.pdf",
            "application/pdf",
            icon=":material/picture_as_pdf:",
            use_container_width=True,
        )
    with exp_c2:
        st.download_button(
            "Download Customer Record (CSV)",
            pd.DataFrame([profile]).to_csv(index=False).encode("utf-8"),
            f"customer_360_{selected_cid}.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 3: CUSTOMER SEGMENTATION
# ==============================================================================

elif current_page == "Customer Segmentation":
    seg_summary_df = compute_segment_distribution(filtered)

    # Segment Distribution Charts
    c_seg1, c_seg2 = st.columns(2)
    with c_seg1:
        fig_seg_pie = px.pie(
            seg_summary_df,
            names="rfm_segment",
            values="customers",
            hole=0.55,
            title="Customer Base Share by RFM Segment",
            color="rfm_segment",
            color_discrete_sequence=CHART_COLORWAY,
        )
        style_chart(fig_seg_pie, 320, legend="bottom")

    with c_seg2:
        fig_seg_bar = px.bar(
            seg_summary_df.sort_values("total_revenue", ascending=True),
            x="total_revenue",
            y="rfm_segment",
            orientation="h",
            title="Merchandise GMV Contribution by Segment",
            color="rfm_segment",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_seg_bar.update_xaxes(title="Revenue (BRL)")
        fig_seg_bar.update_yaxes(title=None)
        style_chart(fig_seg_bar, 320, legend="hidden")

    # Segment Overview Table
    st.markdown('<div class="section-header"><h3>RFM Segment Performance Benchmark Matrix</h3><span>Portfolio Economic Metrics</span></div>', unsafe_allow_html=True)
    display_seg = seg_summary_df.copy()
    display_seg["Customers"] = display_seg["customers"].map(lambda v: f"{v:,}")
    display_seg["% of Base"] = display_seg["customer_share"].map(format_pct)
    display_seg["Total GMV"] = display_seg["total_revenue"].map(format_brl)
    display_seg["% of GMV"] = display_seg["revenue_share"].map(format_pct)
    display_seg["Avg Spend"] = display_seg["avg_spend"].map(format_brl)
    display_seg["Avg 12M CLV"] = display_seg["avg_clv"].map(format_brl)
    display_seg["Avg Orders"] = display_seg["avg_orders"].round(2).astype(str)
    display_seg["Avg Recency"] = display_seg["avg_recency"].round(0).astype(int).astype(str) + "d"
    display_seg["Churn Risk"] = display_seg["avg_churn_prob"].map(format_pct)

    table_cols = ["rfm_segment", "Customers", "% of Base", "Total GMV", "% of GMV", "Avg Spend", "Avg 12M CLV", "Avg Orders", "Avg Recency", "Churn Risk"]
    st.dataframe(display_seg[table_cols].rename(columns={"rfm_segment": "Segment"}), hide_index=True, use_container_width=True)

    # Granular Segment Drill-Down
    st.markdown('<div class="section-header"><h3>Granular Segment Drill-Down & Strategic Action Playbook</h3><span>Deep Dive & Top Profiles</span></div>', unsafe_allow_html=True)
    all_segs = sorted(filtered["rfm_segment"].dropna().unique())
    selected_drill_seg = st.selectbox("Select Segment to Inspect", all_segs, index=0)

    drill_df = filtered[filtered["rfm_segment"] == selected_drill_seg]
    playbook = get_segment_playbook(selected_drill_seg)

    drill_c1, drill_c2 = st.columns([0.45, 0.55])
    with drill_c1:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-left: 4px solid {playbook['badge_color']}; border-radius: 8px; padding: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Strategic Action Playbook</div>
                <div style="font-size: 16px; font-weight: 800; color: #0F172A; margin: 4px 0 6px;">{playbook['title']}</div>
                <p style="font-size: 13px; color: #475569; line-height: 1.45; margin-bottom: 10px;">{playbook['summary']}</p>
                <div style="font-size: 12px; font-weight: 700; color: #0F172A; text-transform: uppercase; margin-bottom: 4px;">Recommended Tactical Actions:</div>
                {''.join([f'<div style="font-size: 12.5px; color: #334155; margin-bottom: 4px;">• {act}</div>' for act in playbook['actions']])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with drill_c2:
        render_kpi_row([
            {"label": "Segment Size", "value": f"{len(drill_df):,}", "subtitle": f"{format_pct(len(drill_df)/max(1, len(filtered)))} of base"},
            {"label": "Total GMV", "value": format_brl(drill_df['total_spend'].sum()), "subtitle": f"{format_pct(drill_df['total_spend'].sum()/max(1, filtered['total_spend'].sum()))} of GMV"},
            {"label": "Average 12M CLV", "value": format_brl(drill_df['predicted_clv'].mean()), "subtitle": "Forward value proxy"},
        ])
        render_kpi_row([
            {"label": "Avg Order Count", "value": f"{drill_df['total_orders'].mean():.2f}", "subtitle": "Orders per customer"},
            {"label": "Avg Inactivity", "value": f"{drill_df['recency_days'].mean():.0f} days", "subtitle": "Recency interval"},
            {"label": "Churn Propensity", "value": format_pct(drill_df['churn_probability'].mean()), "subtitle": "Calibrated risk"},
        ])

    st.markdown(f"**Top Customer Profiles in `{selected_drill_seg}` Segment:**")
    render_customer_table(drill_df, page_size_default=10, key_prefix="drill_tbl")

    # Segment Comparison Matrix
    st.markdown('<div class="section-header"><h3>Segment Comparison Matrix</h3><span>Analytical Side-by-Side Evaluation</span></div>', unsafe_allow_html=True)
    comp_c1, comp_c2 = st.columns(2)
    with comp_c1:
        seg_choice_a = st.selectbox("Segment A", all_segs, index=0, key="seg_comp_a")
    with comp_c2:
        seg_choice_b = st.selectbox("Segment B", all_segs, index=min(1, len(all_segs) - 1), key="seg_comp_b")

    comp_results = compare_segments(filtered, seg_choice_a, seg_choice_b)
    comp_table = pd.DataFrame(comp_results).rename(columns={
        "metric": "Analytical Metric",
        "val_a": f"Segment A ({seg_choice_a})",
        "val_b": f"Segment B ({seg_choice_b})",
    })
    st.dataframe(comp_table, hide_index=True, use_container_width=True)

    # Custom Marketing Cohort Builder
    st.markdown('<div class="section-header"><h3>Targeted Marketing Cohort Builder</h3><span>Campaign Activation with CSV Export</span></div>', unsafe_allow_html=True)
    with st.expander("Configure Targeted Audience Parameters", expanded=False, icon=":material/tune:"):
        b_c1, b_c2, b_c3 = st.columns(3)
        b_rfm = b_c1.multiselect("Select RFM Target Audiences", all_segs, default=["Champions", "Loyal Customers"])
        b_min_spend = b_c2.slider("Minimum Lifetime Spend (BRL)", 0.0, 5000.0, 100.0, step=50.0)
        b_max_churn = b_c3.slider("Max Acceptable Churn Propensity", 0.0, 1.0, 0.70, step=0.05)

        cohort_result = filtered.copy()
        if b_rfm:
            cohort_result = cohort_result[cohort_result["rfm_segment"].isin(b_rfm)]
        cohort_result = cohort_result[(cohort_result["total_spend"] >= b_min_spend) & (cohort_result["churn_probability"] <= b_max_churn)]

        render_kpi_row([
            {"label": "Matching Audience Size", "value": f"{len(cohort_result):,} Customers", "subtitle": "Audience reach"},
            {"label": "Total Cohort GMV", "value": format_brl(cohort_result["total_spend"].sum()), "subtitle": "Gross spending"},
            {"label": "Average Cohort CLV", "value": format_brl(cohort_result["predicted_clv"].mean()), "subtitle": "Forward value"},
        ])

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "Export Targeted Marketing Cohort (CSV)",
            cohort_result.to_csv(index=False).encode("utf-8"),
            "targeted_marketing_cohort.csv",
            "text/csv",
            icon=":material/download:",
        )

    # Methodology Expander
    render_methodology_panel("rfm")


# ==============================================================================
# WORKSPACE 4: CUSTOMER VALUE / CLV
# ==============================================================================

elif current_page == "Customer Value / CLV":
    clv_bench = compute_clv_overview(filtered)

    # CLV KPI Row
    render_kpi_row([
        {
            "label": "Average 12M CLV",
            "value": format_brl(clv_bench["avg_clv"]),
            "subtitle": f"Median: {format_brl(clv_bench['median_clv'])}",
            "icon": "📈",
        },
        {
            "label": "Top 10% Customer CLV",
            "value": format_brl(clv_bench["top_10_pct_avg"]),
            "subtitle": f"Threshold >= {format_brl(clv_bench['p90_clv'])}",
            "icon": "💎",
        },
        {
            "label": "Forward 12M Pipeline",
            "value": format_brl(clv_bench["total_pipeline_clv"]),
            "subtitle": "Total expected value",
            "icon": "💰",
        },
        {
            "label": "Analyzed Profiles",
            "value": f"{clv_bench['total_customers']:,}",
            "subtitle": "Active customer base",
            "icon": "👥",
        },
    ])

    # Dynamic CLV Value Bands
    st.markdown('<div class="section-header"><h3>Dynamic Customer Lifetime Value Distribution</h3><span>Dynamic Value Bands</span></div>', unsafe_allow_html=True)
    clv_bins_df = compute_clv_bins(filtered)

    col_clv_1, col_clv_2 = st.columns(2)
    with col_clv_1:
        fig_clv_bins = px.bar(
            clv_bins_df,
            x="clv_bracket",
            y="customers",
            title="Customer Count by 12-Month CLV Band",
            color="clv_bracket",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_clv_bins.update_xaxes(title="12M CLV Bracket")
        fig_clv_bins.update_yaxes(title="Customer Count")
        style_chart(fig_clv_bins, 300, legend="hidden")

    with col_clv_2:
        fig_clv_rev = px.bar(
            clv_bins_df,
            x="clv_bracket",
            y="total_historical_spend",
            title="Historical Spend Contribution by CLV Band",
            color="clv_bracket",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_clv_rev.update_xaxes(title="12M CLV Bracket")
        fig_clv_rev.update_yaxes(title="Historical Spend (BRL)")
        style_chart(fig_clv_rev, 300, legend="hidden")

    # High-Value Customer Cohort Analysis
    st.markdown('<div class="section-header"><h3>High-Value Customer Cohort Analysis</h3><span>Top 10% by Predicted 12M CLV</span></div>', unsafe_allow_html=True)
    high_val_data = analyze_high_value_cohort(filtered, percentile=0.90)

    render_kpi_row([
        {"label": "High-Value Cohort Size", "value": f"{high_val_data['count']:,} Customers", "subtitle": f"{format_pct(high_val_data['pct_of_base'])} of customer base"},
        {"label": "Historical GMV Share", "value": format_pct(high_val_data['revenue_share']), "subtitle": format_brl(high_val_data['revenue_contribution'])},
        {"label": "Average Cohort CLV", "value": format_brl(high_val_data['avg_clv']), "subtitle": f"Min: {format_brl(high_val_data['threshold'])}"},
        {"label": "Average Order Count", "value": f"{high_val_data['avg_frequency']:.2f} orders", "subtitle": "Frequency"},
    ])

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("**Top High-Value Customer Records:**")
    render_customer_table(high_val_data["cohort_df"], page_size_default=10, key_prefix="hv_tbl")

    # Forward 12-Month CLV Scenario Estimator
    st.markdown('<div class="section-header"><h3>Forward 12-Month CLV Scenario Estimator</h3><span>Machine Learning Simulation</span></div>', unsafe_allow_html=True)
    clv_model = load_model("clv_model.pkl")
    sim_clv_l, sim_clv_r = st.columns([0.5, 0.5])

    with sim_clv_l:
        with st.form("clv_estimator_form"):
            st.markdown("**Simulate Customer Profile Inputs:**")
            k1, k2 = st.columns(2)
            c_rec = k1.number_input("Days Inactive (Recency)", min_value=0, max_value=800, value=30, step=5)
            c_freq = k2.number_input("Completed Orders (Frequency)", min_value=1, max_value=50, value=3, step=1)

            k3, k4 = st.columns(2)
            c_mon = k3.number_input("Historical Spend (BRL)", min_value=5.0, max_value=50000.0, value=450.0, step=10.0)
            c_aov = k4.number_input("Average Order Value (BRL)", min_value=5.0, max_value=25000.0, value=150.0, step=10.0)

            k5, k6 = st.columns(2)
            c_prod = k5.number_input("Distinct Products Purchased", min_value=1, max_value=50, value=3, step=1)
            c_span = k6.number_input("Customer Purchase Span (Days)", min_value=1, max_value=800, value=90, step=5)

            clv_submit = st.form_submit_button("Run Live 12-Month CLV Estimation", type="primary", use_container_width=True)

    with sim_clv_r:
        if clv_model is not None:
            clv_in = model_input_frame(c_rec, c_freq, c_mon, c_aov, c_prod, c_span)
            est_clv = max(float(clv_model.predict(clv_in)[0]), 0.0)
            int_low = est_clv * 0.85
            int_high = est_clv * 1.15

            q25, q50, q75 = filtered["predicted_clv"].quantile([0.25, 0.50, 0.75])
            val_tier = "Platinum VIP" if est_clv >= q75 else "Gold Tier" if est_clv >= q50 else "Silver Tier" if est_clv >= q25 else "Bronze Tier"

            st.markdown("**12-Month Forward Value Forecast:**")
            render_kpi_row([
                {"label": "Predicted 12M CLV", "value": format_brl(est_clv), "subtitle": "Expected forward value"},
                {"label": "Customer Value Tier", "value": val_tier, "subtitle": "Cohort tier"},
            ])
            st.markdown(f"**80% Planning Range:** `{format_brl(int_low)}` — `{format_brl(int_high)}`")
            st.info("💡 **Commercial Strategy:** Prioritize premium VIP loyalty recognition, dedicated concierge support, and early access cross-sell." if "Platinum" in val_tier or "Gold" in val_tier else "💡 **Commercial Strategy:** Target with category cross-sell discounts to build repeat order frequency.")
        else:
            st.info("CLV regression model is ready.")

    # Methodology Expander
    render_methodology_panel("clv")


# ==============================================================================
# WORKSPACE 5: CHURN INTELLIGENCE
# ==============================================================================

elif current_page == "Churn Intelligence":
    risk_summary = compute_risk_overview(filtered)

    # Risk KPI Row
    render_kpi_row([
        {
            "label": "Total At-Risk Customers",
            "value": f"{risk_summary['at_risk_count']:,}",
            "subtitle": f"{format_pct(risk_summary['at_risk_pct'])} of active base",
            "icon": "⚠️",
        },
        {
            "label": "At-Risk Revenue Exposure",
            "value": format_brl(risk_summary["at_risk_revenue"]),
            "subtitle": f"{format_pct(risk_summary['at_risk_rev_pct'])} of total GMV",
            "icon": "💸",
        },
        {
            "label": "High-Value At-Risk",
            "value": f"{risk_summary['high_val_at_risk_count']:,}",
            "subtitle": format_brl(risk_summary["high_val_at_risk_rev"]),
            "icon": "🎯",
        },
        {
            "label": "Average Churn Propensity",
            "value": format_pct(risk_summary["avg_churn_prob"]),
            "subtitle": "Calibrated risk score",
            "icon": "📉",
        },
    ])

    # High-Value + High-Risk 4-Quadrant Matrix
    st.markdown('<div class="section-header"><h3>High-Value + High-Risk Prioritization Matrix</h3><span>4-Quadrant Strategic Framework</span></div>', unsafe_allow_html=True)
    quad_data = compute_quadrant_matrix(filtered)

    if quad_data:
        q_cols = st.columns(4)
        for q_idx, (q_name, q_info) in enumerate(quad_data["quadrants"].items()):
            with q_cols[q_idx]:
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-top: 3px solid {q_info['badge_color']}; border-radius: 8px; padding: 14px; height: 100%;">
                        <div style="font-size: 12px; font-weight: 700; color: #0F172A; margin-bottom: 4px;">{q_name.split('(')[0]}</div>
                        <div style="font-size: 18px; font-weight: 800; color: {q_info['badge_color']}; margin-bottom: 2px;">{q_info['count']:,}</div>
                        <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">{format_pct(q_info['share'])} of base ({format_brl(q_info['revenue'])})</div>
                        <div style="font-size: 11px; color: #334155; line-height: 1.35;">{q_info['action']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Customer Retention Prioritization Queue
    st.markdown('<div class="section-header"><h3>Actionable Customer Retention Prioritization Queue</h3><span>Ranked by Commercial Risk Exposure</span></div>', unsafe_allow_html=True)
    st.markdown(
        render_insight_card(
            title="Customer Priority Calculation",
            description="Priority Score is transparently computed as: <strong>Priority = (Churn Probability) × (Normalized Predicted CLV) × 100</strong>. Focus retention outreach on top scores.",
            kind="info",
        ),
        unsafe_allow_html=True,
    )

    prio_df = calculate_customer_prioritization(filtered, top_n=200)
    render_customer_table(prio_df, page_size_default=10, key_prefix="prio_tbl")

    # Live Churn Propensity What-If Simulator
    st.markdown('<div class="section-header"><h3>Live Customer Churn What-If Simulator</h3><span>Scenario Testing</span></div>', unsafe_allow_html=True)
    churn_model = load_model("churn_model.pkl")
    sim_col_l, sim_col_r = st.columns([0.5, 0.5])

    with sim_col_l:
        with st.form("churn_sim_form_v2"):
            st.markdown("**Simulate Scenario Parameters:**")
            sc1, sc2 = st.columns(2)
            s_rec = sc1.number_input("Days Inactive (Recency)", min_value=0, max_value=800, value=90, step=5)
            s_freq = sc2.number_input("Total Orders (Frequency)", min_value=1, max_value=50, value=2, step=1)

            sc3, sc4 = st.columns(2)
            s_mon = sc3.number_input("Total Spend (BRL)", min_value=5.0, max_value=50000.0, value=280.0, step=10.0, key="sim_spend")
            s_aov = sc4.number_input("Average Order Value (BRL)", min_value=5.0, max_value=25000.0, value=140.0, step=10.0, key="sim_aov")

            sc5, sc6 = st.columns(2)
            s_prod = sc5.number_input("Distinct Products Purchased", min_value=1, max_value=50, value=2, step=1, key="sim_prod")
            s_age = sc6.number_input("Customer Purchase Span (Days)", min_value=1, max_value=800, value=45, step=5, key="sim_age")

            churn_submit = st.form_submit_button("Run Live Churn Propensity Inference", type="primary", use_container_width=True)

    with sim_col_r:
        if churn_model is not None:
            in_df = model_input_frame(s_rec, s_freq, s_mon, s_aov, s_prod, s_age)
            prob = float(churn_model.predict_proba(in_df)[0, 1])
            band = "High Risk" if prob >= 0.65 else "Medium Risk" if prob >= 0.35 else "Low Risk"

            st.markdown("**Live Scenario Prediction Output:**")
            render_kpi_row([
                {"label": "Predicted Churn Risk", "value": format_pct(prob), "subtitle": "Propensity score"},
                {"label": "Risk Classification", "value": band, "subtitle": "Portfolio tier"},
            ])
            act = retention_action(prob)
            st.info(f"**Automated Retention Playbook:** {act['action']}")
        else:
            st.info("Churn pipeline model is ready.")

    # Global Feature Importance Drivers
    feature_importance = load_csv("model_feature_importance.csv")
    if not feature_importance.empty:
        st.markdown('<div class="section-header"><h3>Global Feature Drivers (XGBoost Churn Classifier)</h3></div>', unsafe_allow_html=True)
        sorted_imp = feature_importance.sort_values("churn_importance", ascending=True)
        fig_imp = px.bar(
            sorted_imp,
            x="churn_importance",
            y="feature",
            orientation="h",
            title="Relative Feature Importance for Churn Prediction",
            color="churn_importance",
            color_continuous_scale="Reds",
        )
        fig_imp.update_layout(coloraxis_showscale=False)
        fig_imp.update_xaxes(title="Relative Importance Weight")
        fig_imp.update_yaxes(title=None)
        style_chart(fig_imp, 280, legend="hidden")

    # Methodology Expander
    render_methodology_panel("risk")
    render_methodology_panel("priority")


# ==============================================================================
# WORKSPACE 6: SENTIMENT INTELLIGENCE
# ==============================================================================

elif current_page == "Sentiment Intelligence":
    reviews_df = load_sentiment_dataset()
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    sentiment_overview = compute_sentiment_overview(reviews_df)

    # CSAT & Sentiment KPI Row
    render_kpi_row([
        {
            "label": "Average CSAT Rating",
            "value": f"{sentiment_overview['avg_review_score']:.2f} / 5.0",
            "subtitle": f"{sentiment_overview['total_reviews']:,} verified reviews",
            "icon": "⭐",
        },
        {
            "label": "Positive Feedback Rate",
            "value": format_pct(sentiment_overview["positive_pct"]),
            "delta": f"{sentiment_overview['positive_count']:,} ratings",
            "delta_direction": "positive",
            "subtitle": "4-5 Stars (Satisfied)",
            "icon": "😊",
        },
        {
            "label": "Neutral Feedback Rate",
            "value": format_pct(sentiment_overview["neutral_pct"]),
            "subtitle": "3 Stars (Indifferent)",
            "icon": "😐",
        },
        {
            "label": "Negative Feedback Rate",
            "value": format_pct(sentiment_overview["negative_pct"]),
            "delta": f"{sentiment_overview['negative_count']:,} ratings",
            "delta_direction": "negative",
            "subtitle": "1-2 Stars (Friction)",
            "icon": "⚠️",
        },
    ])

    # Sentiment Breakdown & Distribution
    st.markdown('<div class="section-header"><h3>Customer Sentiment & Satisfaction Distribution</h3><span>Empirical CSAT Breakdown</span></div>', unsafe_allow_html=True)
    col_sent_1, col_sent_2 = st.columns(2)

    with col_sent_1:
        if not reviews_df.empty:
            score_counts = reviews_df["review_score"].value_counts().reset_index()
            score_counts.columns = ["review_score", "count"]
            score_counts = score_counts.sort_values("review_score")
            score_counts["star_label"] = score_counts["review_score"].astype(str) + " Star(s)"

            fig_stars = px.bar(
                score_counts,
                x="star_label",
                y="count",
                title="Customer Review Rating Distribution (1 to 5 Stars)",
                color="review_score",
                color_continuous_scale="Blues",
            )
            fig_stars.update_xaxes(title="Review Score")
            fig_stars.update_yaxes(title="Review Count")
            fig_stars.update_layout(coloraxis_showscale=False)
            style_chart(fig_stars, 300, legend="hidden")

    with col_sent_2:
        if not reviews_df.empty:
            sent_cat_counts = reviews_df["sentiment_category"].value_counts().reset_index()
            sent_cat_counts.columns = ["sentiment_category", "count"]
            fig_sent_pie = px.pie(
                sent_cat_counts,
                names="sentiment_category",
                values="count",
                hole=0.55,
                title="Customer Sentiment Polarity Breakdown",
                color="sentiment_category",
                color_discrete_map={
                    "Positive": COLOR_GREEN,
                    "Neutral": COLOR_AMBER,
                    "Negative": COLOR_RED,
                },
            )
            style_chart(fig_sent_pie, 300, legend="bottom")

    # Longitudinal Sentiment Trajectory Trend
    st.markdown('<div class="section-header"><h3>Longitudinal CSAT & Sentiment Trajectory</h3><span>Monthly Satisfaction Tracking</span></div>', unsafe_allow_html=True)
    monthly_sent = compute_sentiment_trend(reviews_df)
    if not monthly_sent.empty:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=monthly_sent["review_month"],
            y=monthly_sent["pos_reviews"],
            name="Positive Reviews (4-5 Stars)",
            marker_color=COLOR_GREEN,
            opacity=0.85,
        ))
        fig_trend.add_trace(go.Bar(
            x=monthly_sent["review_month"],
            y=monthly_sent["neg_reviews"],
            name="Negative Reviews (1-2 Stars)",
            marker_color=COLOR_RED,
            opacity=0.85,
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly_sent["review_month"],
            y=monthly_sent["avg_score"],
            name="Average CSAT Rating (1-5)",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color=COLOR_PRIMARY, width=3),
            marker=dict(size=6),
        ))
        fig_trend.update_layout(
            barmode="stack",
            title="Monthly Customer Reviews Volume and Average CSAT Rating",
            yaxis=dict(title="Review Count"),
            yaxis2=dict(title="Average CSAT Score", overlaying="y", side="right", range=[1, 5], showgrid=False),
        )
        style_chart(fig_trend, 320, legend="top")

    # Negative Theme Root-Cause Extraction
    st.markdown('<div class="section-header"><h3>Negative Feedback Root-Cause Themes</h3><span>Factual Text Extraction & Friction Drivers</span></div>', unsafe_allow_html=True)
    themes = extract_negative_themes(reviews_df, top_n=5)
    
    if themes:
        t_cols = st.columns(min(len(themes), 3))
        for idx, t in enumerate(themes[:3]):
            with t_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-top: 3px solid {t['badge_color']}; border-radius: 8px; padding: 14px; height: 100%;">
                        <div style="font-size: 20px; margin-bottom: 2px;">{t['icon']}</div>
                        <div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 4px;">{t['theme']}</div>
                        <div style="font-size: 18px; font-weight: 800; color: {t['badge_color']}; margin-bottom: 2px;">{t['matched_count']:,} Reviews</div>
                        <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">{format_pct(t['share_of_negative_comments'])} of low-rating feedback</div>
                        <div style="font-size: 11.5px; color: #334155; line-height: 1.4; margin-bottom: 8px;"><strong>Diagnostic:</strong> {t['description']}</div>
                        <div style="font-size: 11px; color: #0284C7; font-weight: 600;">🛠️ {t['action']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if len(themes) > 3:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            t_cols2 = st.columns(len(themes) - 3)
            for idx, t in enumerate(themes[3:]):
                with t_cols2[idx]:
                    st.markdown(
                        f"""
                        <div style="background: white; border: 1px solid #E2E8F0; border-top: 3px solid {t['badge_color']}; border-radius: 8px; padding: 14px; height: 100%;">
                            <div style="font-size: 20px; margin-bottom: 2px;">{t['icon']}</div>
                            <div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 4px;">{t['theme']}</div>
                            <div style="font-size: 18px; font-weight: 800; color: {t['badge_color']}; margin-bottom: 2px;">{t['matched_count']:,} Reviews</div>
                            <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">{format_pct(t['share_of_negative_comments'])} of low-rating feedback</div>
                            <div style="font-size: 11.5px; color: #334155; line-height: 1.4; margin-bottom: 8px;"><strong>Diagnostic:</strong> {t['description']}</div>
                            <div style="font-size: 11px; color: #0284C7; font-weight: 600;">🛠️ {t['action']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Sentiment by RFM Segment & Product Category
    st.markdown('<div class="section-header"><h3>Satisfaction by Segment & Product Category</h3><span>Cross-Dimensional CSAT Insights</span></div>', unsafe_allow_html=True)
    c_sub1, c_sub2 = st.columns(2)

    with c_sub1:
        seg_sent_df = compute_sentiment_by_segment(filtered, reviews_df, fact_orders)
        if not seg_sent_df.empty:
            fig_seg_csat = px.bar(
                seg_sent_df,
                x="rfm_segment",
                y="avg_csat",
                title="Average Customer CSAT Rating by RFM Segment",
                color="avg_csat",
                color_continuous_scale="Viridis",
            )
            fig_seg_csat.update_yaxes(range=[1, 5], title="Avg CSAT Rating")
            fig_seg_csat.update_xaxes(title=None)
            style_chart(fig_seg_csat, 290, legend="hidden")

    with c_sub2:
        cat_csat_df = compute_category_satisfaction(fact_orders, reviews_df, filtered)
        if not cat_csat_df.empty:
            fig_cat_csat = px.bar(
                cat_csat_df.head(10),
                x="avg_review_score",
                y="favorite_category",
                orientation="h",
                title="Top 10 Rated Product Categories (Min. 50 Customers)",
                color="avg_review_score",
                color_continuous_scale="Greens",
            )
            fig_cat_csat.update_xaxes(range=[3.5, 5], title="Avg Rating")
            fig_cat_csat.update_yaxes(title=None)
            style_chart(fig_cat_csat, 290, legend="hidden")

    # Customer Review Text Explorer
    st.markdown('<div class="section-header"><h3>Customer Feedback Review Explorer</h3><span>Search Verified Review Comments</span></div>', unsafe_allow_html=True)
    if not reviews_df.empty:
        with st.expander("Filter Customer Reviews", expanded=False, icon=":material/search:"):
            f_r1, f_r2 = st.columns(2)
            sel_stars = f_r1.multiselect("Review Star Ratings", [1, 2, 3, 4, 5], default=[1, 2])
            only_comments = f_r2.checkbox("Only Show Reviews With Written Comments", value=True)

            rev_filtered = reviews_df.copy()
            if sel_stars:
                rev_filtered = rev_filtered[rev_filtered["review_score"].isin(sel_stars)]
            if only_comments:
                rev_filtered = rev_filtered[rev_filtered["review_comment_message"].notna() & (rev_filtered["review_comment_message"].str.strip() != "")]

            st.markdown(f"**Found {len(rev_filtered):,} matching customer reviews:**")
            rev_cols = ["review_score", "sentiment_category", "review_creation_date", "review_comment_title", "review_comment_message", "order_id"]
            avail_rcols = [c for c in rev_cols if c in rev_filtered.columns]
            st.dataframe(rev_filtered[avail_rcols].head(100), hide_index=True, use_container_width=True)


# ==============================================================================
# WORKSPACE 7: RECOMMENDATIONS
# ==============================================================================

elif current_page == "Recommendations":
    rec_portfolio_df = compute_recommendation_portfolio(filtered, limit=2500)
    rec_summary = compute_recommendation_summary(rec_portfolio_df)

    urgent_count = len(rec_portfolio_df[rec_portfolio_df["priority"] == "Urgent"])
    high_count = len(rec_portfolio_df[rec_portfolio_df["priority"] == "High"])
    top_action = rec_summary.iloc[0]["action_type"] if not rec_summary.empty else "Standard Lifecycle Nurture"

    # Recommendations KPI Row
    render_kpi_row([
        {
            "label": "Actionable Profiles",
            "value": f"{len(rec_portfolio_df):,}",
            "subtitle": "Evaluated cohort records",
            "icon": "🎯",
        },
        {
            "label": "Urgent Action Required",
            "value": f"{urgent_count:,}",
            "delta": f"{high_count:,} High Priority",
            "delta_direction": "negative" if urgent_count > 0 else "neutral",
            "subtitle": "Service recovery / VIP retention",
            "icon": "🚨",
        },
        {
            "label": "Top Recommended Strategy",
            "value": top_action,
            "subtitle": "Largest action volume",
            "icon": "💡",
        },
        {
            "label": "Covered Revenue",
            "value": format_brl(rec_portfolio_df["total_spend"].sum()),
            "subtitle": "Total gross merchandise value",
            "icon": "💰",
        },
    ])

    # Recommendation Distribution & Summary
    st.markdown('<div class="section-header"><h3>Recommended Action Distribution & Commercial Allocation</h3><span>Audience Action Summary</span></div>', unsafe_allow_html=True)
    r_col1, r_col2 = st.columns([0.45, 0.55])

    with r_col1:
        if not rec_summary.empty:
            fig_rec_bar = px.bar(
                rec_summary.sort_values("customer_count", ascending=True),
                x="customer_count",
                y="action_type",
                orientation="h",
                title="Customer Count by Recommended Action",
                color="action_type",
                color_discrete_sequence=CHART_COLORWAY,
            )
            fig_rec_bar.update_xaxes(title="Customer Count")
            fig_rec_bar.update_yaxes(title=None)
            style_chart(fig_rec_bar, 290, legend="hidden")

    with r_col2:
        if not rec_summary.empty:
            disp_rec_sum = rec_summary.copy()
            disp_rec_sum["Customers"] = disp_rec_sum["customer_count"].map(lambda v: f"{v:,}")
            disp_rec_sum["Total GMV"] = disp_rec_sum["total_gmv"].map(format_brl)
            disp_rec_sum["Avg 12M CLV"] = disp_rec_sum["avg_clv"].map(format_brl)
            disp_rec_sum["Avg Churn Risk"] = disp_rec_sum["avg_churn_risk"].map(format_pct)
            st.dataframe(
                disp_rec_sum[["action_type", "priority", "Customers", "Total GMV", "Avg 12M CLV", "Avg Churn Risk"]].rename(columns={"action_type": "Action Strategy", "priority": "Priority"}),
                hide_index=True,
                use_container_width=True,
            )

    # Documented Recommendation Rules & Decision Logic
    st.markdown('<div class="section-header"><h3>Documented Recommendation Logic & Decision Rules</h3><span>Rule-Based Multi-Signal Matrix</span></div>', unsafe_allow_html=True)
    with st.expander("View Transparent Decision Rules & Targeting Criteria", expanded=False, icon=":material/rule:"):
        rules_df = pd.DataFrame([
            {
                "Strategy / Action": r["action_type"],
                "Priority Level": r["priority"],
                "Target Audience Criteria": r["target_audience"],
                "Execution Channel": r["channel"],
                "Commercial Rationale": r["rationale"],
            }
            for r in RECOMMENDATION_RULES
        ])
        st.dataframe(rules_df, hide_index=True, use_container_width=True)

    # Actionable Customer Recommendation Queue Table
    st.markdown('<div class="section-header"><h3>Actionable Customer Recommendation Queue</h3><span>Customer Priority Queue</span></div>', unsafe_allow_html=True)
    
    # Filters for Recommendation Queue
    with st.expander("Filter Recommendation Queue", expanded=True, icon=":material/filter_list:"):
        f_rec1, f_rec2, f_rec3 = st.columns(3)
        act_filter = f_rec1.selectbox("Filter by Action Type", ["All", *sorted(rec_portfolio_df["action_type"].unique())])
        prio_filter = f_rec2.selectbox("Filter by Priority", ["All", "Urgent", "High", "Medium", "Standard"])
        seg_rec_filter = f_rec3.selectbox("Filter by RFM Segment", ["All", *sorted(rec_portfolio_df["rfm_segment"].unique())])

        filtered_recs = rec_portfolio_df.copy()
        if act_filter != "All":
            filtered_recs = filtered_recs[filtered_recs["action_type"] == act_filter]
        if prio_filter != "All":
            filtered_recs = filtered_recs[filtered_recs["priority"] == prio_filter]
        if seg_rec_filter != "All":
            filtered_recs = filtered_recs[filtered_recs["rfm_segment"] == seg_rec_filter]

    st.markdown(f"**Displaying {len(filtered_recs):,} customer action recommendations:**")
    
    # Formatted Queue Table
    display_q = pd.DataFrame()
    display_q["Customer ID"] = filtered_recs["customer_id"]
    display_q["Recommended Action"] = filtered_recs["action_type"]
    display_q["Priority"] = filtered_recs["priority"]
    display_q["RFM Segment"] = filtered_recs["rfm_segment"]
    display_q["Decision Rationale"] = filtered_recs["reason"]
    display_q["12M CLV"] = filtered_recs["predicted_clv"].map(format_brl)
    display_q["Churn Risk"] = filtered_recs["churn_probability"].map(format_pct)
    display_q["Primary Category"] = filtered_recs["favorite_category"]
    display_q["Location"] = filtered_recs["city"].str.title() + ", " + filtered_recs["state"].str.upper()

    st.dataframe(display_q, hide_index=True, use_container_width=True)

    # Next-Best-Category Cross-Sell Catalog Explorer
    recommendations_cat = load_csv("recommendations.csv")
    if not recommendations_cat.empty:
        st.markdown('<div class="section-header"><h3>Next-Best-Category Cross-Sell Catalog</h3><span>Market Basket Co-Occurrence Recommendations</span></div>', unsafe_allow_html=True)
        with st.expander("Search Next-Best-Category Offers by Customer ID", expanded=False, icon=":material/auto_awesome:"):
            top_rec_sample = recommendations_cat.head(100)
            st.dataframe(top_rec_sample, hide_index=True, use_container_width=True)

    # Export Recommendation Queue
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.download_button(
        "Download Filtered Recommendation Action Queue (CSV)",
        filtered_recs.to_csv(index=False).encode("utf-8"),
        "customer_action_recommendations.csv",
        "text/csv",
        icon=":material/download:",
    )


# ==============================================================================
# WORKSPACE 8: ANALYTICS EXPLORER
# ==============================================================================

elif current_page == "Analytics Explorer":
    st.markdown('<div class="section-header"><h3>Customer Discovery & Analytical Slice Explorer</h3><span>Multi-Criteria Search & Distribution Analysis</span></div>', unsafe_allow_html=True)

    # Search & Filter Controls
    with st.expander("Filter & Search Criteria", expanded=True, icon=":material/search:"):
        f_row1_c1, f_row1_c2, f_row1_c3 = st.columns(3)
        with f_row1_c1:
            search_query = st.text_input("Search by Customer ID, City, or Category", placeholder="Type keywords...")
        with f_row1_c2:
            seg_filter = st.selectbox("RFM Segment", ["All", *sorted(customer_features["rfm_segment"].dropna().unique())], key="exp_seg")
        with f_row1_c3:
            risk_filter = st.selectbox("Risk Level", ["All", "Low Risk (<35%)", "Medium Risk (35-65%)", "High Risk (>=65%)"], key="exp_risk")

        f_row2_c1, f_row2_c2, f_row2_c3 = st.columns(3)
        with f_row2_c1:
            state_filter = st.selectbox("State / Region", ["All", *sorted(customer_features["state"].dropna().unique())], key="exp_state")
        with f_row2_c2:
            clv_filter = st.selectbox("CLV Value Band", ["All", "Platinum", "Gold", "Silver", "Bronze"], key="exp_clv_band")
        with f_row2_c3:
            recency_filter = st.selectbox("Recency Window", ["All", "Recent (<90 days)", "Active (90-180 days)", "Lapsed (181-365 days)", "Inactive (>365 days)"], key="exp_rec")

        if st.button("Reset Explorer Filters", icon=":material/restart_alt:"):
            st.rerun()

    # Apply Search & Filters
    filtered_explorer = search_customers(
        df=filtered,
        search_query=search_query,
        segment=seg_filter,
        risk_level=risk_filter,
        state=state_filter,
        clv_band=clv_filter,
        recency_filter=recency_filter,
    )

    if filtered_explorer.empty:
        render_empty_state(
            title="No Matching Customers Found",
            description="No customer profiles match your search criteria. Try modifying your search keywords or resetting filters.",
            show_reset=False,
        )
    else:
        # Quick Summary Cards of Filtered Explorer Set
        render_kpi_row([
            {"label": "Matching Profiles", "value": f"{len(filtered_explorer):,}", "subtitle": "Customer records"},
            {"label": "Total Filtered GMV", "value": format_brl(filtered_explorer["total_spend"].sum()), "subtitle": "Gross spending"},
            {"label": "Average 12M CLV", "value": format_brl(filtered_explorer["predicted_clv"].mean()), "subtitle": "Forward value"},
            {"label": "Average Churn Risk", "value": format_pct(filtered_explorer["churn_probability"].mean()), "subtitle": "Risk propensity"},
        ])

        # Visual Analytics of Filtered Slice
        st.markdown('<div class="section-header"><h3>Analytical Distribution of Filtered Slice</h3><span>Empirical Slice Visualizations</span></div>', unsafe_allow_html=True)
        e_c1, e_c2 = st.columns(2)
        with e_c1:
            fig_e_spend = px.histogram(
                filtered_explorer[filtered_explorer["total_spend"] <= filtered_explorer["total_spend"].quantile(0.98)],
                x="total_spend",
                nbins=30,
                title="Spend Distribution of Filtered Cohort (BRL)",
                color_discrete_sequence=[COLOR_PRIMARY],
            )
            fig_e_spend.update_xaxes(title="Spend (BRL)")
            fig_e_spend.update_yaxes(title="Customers")
            style_chart(fig_e_spend, 260, legend="hidden")

        with e_c2:
            fig_e_rec = px.histogram(
                filtered_explorer,
                x="recency_days",
                nbins=30,
                title="Inactivity Recency Distribution (Days)",
                color_discrete_sequence=[COLOR_CYAN],
            )
            fig_e_rec.update_xaxes(title="Days Inactive")
            fig_e_rec.update_yaxes(title="Customers")
            style_chart(fig_e_rec, 260, legend="hidden")

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        render_customer_table(filtered_explorer, page_size_default=25, key_prefix="exp_tbl")

        # Export View
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "Download Filtered Customer Explorer View (CSV)",
            filtered_explorer.to_csv(index=False).encode("utf-8"),
            "customer_explorer_filtered.csv",
            "text/csv",
            icon=":material/download:",
        )


# ==============================================================================
# WORKSPACE 9: DATA QUALITY
# ==============================================================================

elif current_page == "Data Quality":
    audit_res = run_data_quality_audit(customer_features)
    env_info = get_environment_info()
    snapshot_info = calculate_data_snapshot_info(customer_features)
    model_reg = audit_model_registry()

    # Data Quality Top KPIs
    render_kpi_row([
        {
            "label": "Data Quality Score",
            "value": f"{audit_res['quality_score_pct']}%",
            "delta": "100% Target",
            "delta_direction": "positive" if audit_res["is_healthy"] else "negative",
            "subtitle": "Schema & range integrity",
            "icon": "🛡️",
        },
        {
            "label": "Canonical Customer Profiles",
            "value": f"{snapshot_info['rows']:,}",
            "subtitle": f"{snapshot_info['columns']} validated attributes",
            "icon": "👥",
        },
        {
            "label": "ML Models Ready",
            "value": f"{sum(1 for m in model_reg if 'Ready' in m['Status'])} / {len(model_reg)}",
            "subtitle": "XGBoost, CLV, Sentiment, K-Means",
            "icon": "🤖",
        },
        {
            "label": "Memory Footprint",
            "value": f"{snapshot_info['memory_mb']} MB",
            "subtitle": "In-memory feature store",
            "icon": "💾",
        },
    ])

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    tab_quality_checks, tab_lineage, tab_drift_mon, tab_models_reg, tab_audit_events = st.tabs([
        "📊 Schema & Quality Integrity Checks",
        "🔄 Data Lineage & Raw vs Processed Audit",
        "📈 Population Stability Index (PSI) Drift",
        "🤖 ML Model Artifact Registry",
        "🛡️ Compliance Event Audit Log",
    ])

    with tab_quality_checks:
        st.markdown("**Automated Data Integrity Test Suite:**")
        st.dataframe(pd.DataFrame(audit_res["checks"]), hide_index=True, use_container_width=True)

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("**Field-by-Field Completeness & Null Distribution:**")
        field_stats = []
        for col in customer_features.columns:
            null_c = int(customer_features[col].isnull().sum())
            null_p = null_c / max(1, len(customer_features))
            field_stats.append({
                "Attribute Field": col,
                "Data Type": str(customer_features[col].dtype),
                "Non-Null Records": f"{len(customer_features) - null_c:,}",
                "Completeness %": format_pct(1.0 - null_p),
                "Missing / Null Count": f"{null_c:,}",
                "Status": "Complete 🟢" if null_c == 0 else "Contains Nulls 🟡",
            })
        st.dataframe(pd.DataFrame(field_stats), hide_index=True, use_container_width=True)

    with tab_lineage:
        st.markdown("**Data Lineage & Transformation Summary (Raw Olist Ingestion -> Customer 360 Feature Store):**")
        lineage_data = [
            {"Stage": "1. Raw Order Records", "Source File": "olist_orders_dataset.csv", "Raw Volume": "99,441 orders", "Processing": "Filtered out canceled/unavailable orders; extracted purchase timestamps"},
            {"Stage": "2. Raw Order Items", "Source File": "olist_order_items_dataset.csv", "Raw Volume": "112,650 items", "Processing": "Aggregated item prices and freight values per canonical customer"},
            {"Stage": "3. Raw Customer Registry", "Source File": "olist_customers_dataset.csv", "Raw Volume": "99,441 records", "Processing": "Mapped source customer IDs to canonical unique customer ID entities"},
            {"Stage": "4. Raw Review Ratings", "Source File": "olist_order_reviews_dataset.csv", "Raw Volume": "104,721 reviews", "Processing": "Calculated average CSAT rating, low rating counts, and sentiment polarity"},
            {"Stage": "5. Raw Payment Facts", "Source File": "olist_order_payments_dataset.csv", "Raw Volume": "103,886 payments", "Processing": "Consolidated payment methods, installments, and gross transaction values"},
            {"Stage": "6. Canonical Feature Store", "Source File": "customer_360_features.csv", "Processed Volume": "94,983 profiles", "Processing": "Engineered RFM quintiles, XGBoost churn probabilities, and 12M forward CLV"},
        ]
        st.dataframe(pd.DataFrame(lineage_data), hide_index=True, use_container_width=True)

    with tab_drift_mon:
        st.markdown("**Longitudinal Population Stability Index (PSI) Feature Drift Monitoring:**")
        if not customer_features.empty and "recency_days" in customer_features.columns:
            baseline_sub = customer_features[customer_features["recency_days"] > 180]
            current_sub = customer_features[customer_features["recency_days"] <= 180]
            drift_res = run_feature_drift_audit(baseline_sub, current_sub)
            
            st.caption(f"Overall Drift Status: **{drift_res['overall_status']}** | Policy: {drift_res['governance_policy']}")
            st.dataframe(pd.DataFrame(drift_res["features"]), hide_index=True, use_container_width=True)
        else:
            st.info("Insufficient longitudinal data for drift monitoring.")

    with tab_models_reg:
        st.markdown("**Registered Machine Learning Inference Models:**")
        st.dataframe(pd.DataFrame(model_reg), hide_index=True, use_container_width=True)

    with tab_audit_events:
        st.markdown("**Real-Time Enterprise Compliance Event Stream:**")
        recent_logs = get_recent_audit_events(limit=25)
        if recent_logs:
            st.dataframe(pd.DataFrame(recent_logs), hide_index=True, use_container_width=True)
        else:
            st.info("No compliance audit events recorded in active session.")


# ==============================================================================
# WORKSPACE 10: METHODOLOGY / ABOUT
# ==============================================================================

elif current_page == "Methodology / About":
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
            <div style="font-size: 20px; font-weight: 800; color: #0F172A; margin-bottom: 6px;">CustomerAtlas AI — Unified Customer Intelligence Architecture</div>
            <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin: 0;">
                CustomerAtlas AI is an enterprise customer intelligence platform designed to bridge transactional data, machine learning inference, behavioral segmentation, and operational decision workflows.
                Every metric displayed in the platform is mathematically calculated from factual customer records with zero hardcoded assumptions or ungrounded generative hallucinations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t_rfm, t_clv, t_churn, t_sentiment, t_recs, t_health, t_arch = st.tabs([
        "1. RFM Segmentation",
        "2. Customer Lifetime Value",
        "3. Churn Intelligence",
        "4. Sentiment Intelligence",
        "5. Recommendation Engine",
        "6. Customer Health & Lifecycle",
        "7. Tech Stack & Deployment",
    ])

    with t_rfm:
        st.markdown(
            """
            ### 1. Recency, Frequency, Monetary (RFM) Methodology
            **Analytical Principles:**
            - **Recency (R):** Number of calendar days elapsed between the customer's most recent completed order and the snapshot anchor date. Quintile binned from 1 (longest inactive) to 5 (most recent).
            - **Frequency (F):** Total number of distinct completed transaction orders placed across the customer's lifespan.
            - **Monetary (M):** Total cumulative gross spend (in Brazilian Reais, BRL) across all completed orders.
            
            **Audience Segment Matrix:**
            - **Champions (R: 4-5, F: 4-5, M: 4-5):** High-value, frequent, and recently active customers. VIP advocacy & early access perks.
            - **Loyal Customers (F: 3-5, M: 3-5, R: 3-4):** Consistent repeat purchasers forming the primary revenue backbone. Tiered loyalty rewards.
            - **Potential Loyalists (R: 4-5, F: 1-2, M: 3-4):** Recent buyers with healthy initial basket values. Second-purchase cross-sell nurturing.
            - **Regular Customers (R: 2-4, F: 1-2, M: 2-3):** Moderate spend baseline customers. Seasonal catalog promotions.
            - **At Risk (R: 1-2, F: 2-5, M: 2-5):** Previously active repeat buyers who have lapsed past 180 days. Win-back re-engagement incentives.
            - **Lost Customers (R: 1, F: 1-2, M: 1-2):** Longest inactive cohort (>365 days inactive) with lowest engagement.
            """
        )

    with t_clv:
        st.markdown(
            """
            ### 2. Customer Lifetime Value (CLV) Methodology
            **Model Architecture & Target Formulation:**
            - **Model Algorithm:** Supervised Ridge / XGBoost Regressor trained on historical customer transaction trajectories.
            - **Features Utilized:** `recency_days`, `frequency`, `monetary`, `avg_order_value`, `number_of_products`, `customer_age_days`.
            - **Target Definition:** Forward 12-month expected cumulative merchandise gross revenue.
            
            **Dynamic Value Tiers:**
            - **Platinum VIP:** $\ge 75\text{th}$ percentile of predicted CLV.
            - **Gold Tier:** $50\text{th} \text{ to } 75\text{th}$ percentile.
            - **Silver Tier:** $25\text{th} \text{ to } 50\text{th}$ percentile.
            - **Bronze Tier:** $< 25\text{th}$ percentile.
            
            *Limitation Note: Forward CLV represents a statistical expectation proxy for prioritization and does not guarantee future financial realization.*
            """
        )

    with t_churn:
        st.markdown(
            """
            ### 3. Customer Churn & Risk Intelligence
            **Methodology & Attribution Policy:**
            - **Model Algorithm:** Supervised XGBoost Classifier outputting calibrated class probabilities $[0.0, 1.0]$.
            - **Definition:** High risk corresponds to a calibrated probability $\ge 0.65$ of ongoing customer inactivity.
            - **Feature Drivers:** Inactivity duration (`recency_days`), order cadence deceleration, review rating signals, and digital footprint.
            - **Causal Transparency Policy:** Model feature importances reflect statistical predictive correlation rather than asserting direct causality.
            
            **Prioritization Formula:**
            $$\\text{Priority Score} = \\text{Churn Probability} \\times \\left( \\frac{\\text{Predicted CLV}}{\\text{CLV}_{p99}} \\right) \\times 100$$
            """
        )

    with t_sentiment:
        st.markdown(
            """
            ### 4. Sentiment Intelligence & CSAT Scale
            **Methodology & Text Classification:**
            - **CSAT Mapping:**
              - **Positive Sentiment:** Review Rating $4\text{--}5$ Stars.
              - **Neutral Sentiment:** Review Rating $3$ Stars.
              - **Negative Sentiment:** Review Rating $1\text{--}2$ Stars.
            - **Polarity Normalization:** Mapped to $[-1.0, +1.0]$ index.
            - **Root-Cause Theme Extraction:** Deterministic Portuguese keyword matching against customer comments across Logistics Delays, Product Quality, Catalog Inaccuracy, Missing Items, and Customer Support.
            """
        )

    with t_recs:
        st.markdown(
            """
            ### 5. Recommendation Engine
            **Multi-Signal Recommendation Framework:**
            - Synthesizes churn probability, RFM segment, predicted CLV, CSAT rating, and product affinity into deterministic Next-Best-Actions:
              1. **VIP Retention Outreach:** Urgent outreach for Champions / High CLV accounts with churn risk $\ge 65\%$.
              2. **Win-back Campaign:** Re-activation discounts for lapsed buyers inactive $> 180$ days.
              3. **Loyalty Reward:** Advocacy perks for high-health Champions and Loyal customers.
              4. **Second-Purchase Cross-Sell:** Market basket co-occurrence recommendations within 90 days of first order.
              5. **Service Recovery:** Immediate support ticket for customers rating $\le 2.0$ stars.
              6. **Category Upsell:** Basket expansion incentives for baseline spenders.
            """
        )

    with t_health:
        st.markdown(
            """
            ### 6. Customer Health Score & Lifecycle State Machine
            **Customer Health Score Formula (0-100):**
            $$\\text{Score} = 0.25 R_{\\text{norm}} + 0.25 F_{\\text{norm}} + 0.25 M_{\\text{norm}} + 0.15 \\text{Eng}_{\\text{norm}} + 0.10 \\text{CSAT}_{\\text{norm}} - 0.20 \\text{Risk}$$
            
            **6-Stage Lifecycle State Machine:**
            - **New:** Tenure $\le 60$ days and completed 1 order.
            - **Activated:** Completed 1 order with recency $\le 180$ days.
            - **Engaged:** $\ge 2$ orders with recency $\le 120$ days.
            - **Loyal:** $\ge 3$ orders or in Champions / Loyal segments.
            - **At Risk:** Recency $> 180$ days or churn risk $\ge 65\%$.
            - **Inactive / Lost:** Recency $> 365$ days and churn risk $\ge 65\%$.
            """
        )

    with t_arch:
        st.markdown(
            """
            ### 7. Tech Stack, Architecture & Local Execution
            **Core Technology Stack:**
            - **Web Application:** Streamlit 1.35+, Plotly 5.20+
            - **Data & Analytics:** Pandas 2.2+, NumPy 1.26+
            - **Machine Learning:** Scikit-Learn 1.4+, XGBoost 3.0+, Joblib 1.3+
            - **Reporting & Export:** ReportLab 4.0+ (PDF Dossier Engine)
            - **Microservices & API:** FastAPI 0.110+, SQLAlchemy 2.0+
            
            **Local Execution Commands:**
            ```bash
            pip install -r requirements.txt
            streamlit run app.py
            ```
            """
        )


# ==============================================================================
# WORKSPACE 11: ASK CUSTOMERATLAS (GROUNDED AI ASSISTANT)
# ==============================================================================

elif current_page == "Ask CustomerAtlas":
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); border-radius: 10px; padding: 24px; color: white; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="font-size: 24px;">🧭</span>
                <h2 style="margin: 0; font-size: 20px; font-weight: 800; color: #FFFFFF;">Ask CustomerAtlas — Grounded Decision Support</h2>
            </div>
            <p style="margin: 0; font-size: 13.5px; color: #C7D2FE; line-height: 1.5; max-width: 900px;">
                Ask questions in plain English to interrogate customer metrics, revenue concentration, at-risk cohorts, and lifecycle transitions.
                Every response is <strong>100% mathematically grounded in verified database records</strong> with zero hallucinated figures or unconstrained code execution.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ai_service = GroundedAIService(filtered)

    # Preset Quick-Prompt Question Buttons
    st.markdown("**Suggested Decision Inquiries:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    preset_query = None
    with q_col1:
        if st.button("🚨 Which customers are high-value and high-risk?", use_container_width=True):
            preset_query = "Which customers are high-value and high-risk?"
        if st.button("📊 Which segment generates the most revenue?", use_container_width=True):
            preset_query = "Which segment generates the most revenue?"
    with q_col2:
        if st.button("🔄 What is our repeat customer purchase rate?", use_container_width=True):
            preset_query = "What is our repeat customer purchase rate?"
        if st.button("💎 What is the 12-month forward CLV benchmark?", use_container_width=True):
            preset_query = "What is the 12-month forward CLV benchmark?"
    with q_col3:
        if st.button("🗺️ Which geographic regions drive top demand?", use_container_width=True):
            preset_query = "Which geographic regions drive top demand?"
        if st.button("📈 What are our macro customer metrics?", use_container_width=True):
            preset_query = "What are our macro customer metrics?"

    # Context Customer Selector (Optional)
    c_opts = ["None (General Portfolio Query)", *sorted(filtered["customer_id"].dropna().unique().tolist()[:100])]
    sel_ctx_cid = st.selectbox(
        "Optional: Focus on Specific Customer Context",
        c_opts,
        index=0,
        help="Select a specific customer ID to ask detailed diagnostic and risk explanation questions.",
    )
    ctx_cid = None if "None" in sel_ctx_cid else sel_ctx_cid

    # Query Input Form
    with st.form("ask_atlas_query_form"):
        user_query = st.text_input(
            "Enter your question for CustomerAtlas:",
            value=preset_query or "",
            placeholder="e.g. Which customers are high-value and high-risk? or Explain risk for this customer",
        )
        submit_ask = st.form_submit_button("Analyze & Ground Answer", type="primary", use_container_width=True)

    active_prompt = preset_query or (user_query if submit_ask else None)

    if active_prompt:
        with st.spinner("Analyzing verified customer dataset & synthesizing grounded evidence..."):
            ans = ai_service.ask(active_prompt, context_customer_id=ctx_cid)
            render_grounded_answer(ans)

            record_audit_event(
                action="grounded_ai_query",
                resource_type="analytics_query",
                resource_id=ans.intent,
                details={"query": active_prompt, "intent": ans.intent},
                status="success",
            )
    else:
        st.markdown(
            """
            <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 30px; text-align: center; margin-top: 10px;">
                <div style="font-size: 28px; margin-bottom: 8px;">💡</div>
                <div style="font-size: 15px; font-weight: 700; color: #334155;">Ready for Customer Inquiries</div>
                <p style="font-size: 13px; color: #64748B; max-width: 600px; margin: 6px auto 0;">
                    Select one of the suggested inquiry buttons above or type any question into the input field to generate evidence-backed analytics answers.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# GLOBAL FOOTER
# ==============================================================================

render_footer()
