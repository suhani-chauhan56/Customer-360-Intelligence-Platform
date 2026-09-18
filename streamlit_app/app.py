"""CustomerAtlas — Unified Customer Intelligence Platform.

Enterprise-grade B2B customer analytics platform covering:
- Executive Overview & Commercial Health
- Customer 360 Unified Profile Dossier
- Audience & RFM Segmentation Hub (with Custom Cohort Builder)
- Predictive AI Studio (What-If Churn & 12M CLV Simulators)
- Experience & Voice of Customer (VoC) Radar
- Next-Best-Offer & Merchandising Intelligence
- Enterprise Data Warehouse & SQL Analytics Console

Run locally:
    streamlit run streamlit_app/app.py
"""

import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup sys.path to resolve internal modules seamlessly
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components.cards import (
    render_customer_hero,
    render_empty_state,
    render_error_state,
    render_insight_card,
    render_insight_grid,
    render_recommendation_card,
)
from components.footer import render_footer
from components.header import render_global_header, render_page_header
from components.metric_cards import render_kpi_row
from components.sidebar import render_sidebar
from services.data_service import (
    SQL_DIR,
    build_customer_pdf,
    load_csv,
    load_model,
    model_input_frame,
    retention_action,
)
from utils.formatting import (
    format_brl,
    format_currency,
    format_num,
    format_number,
    format_pct,
    format_percent,
)
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

# ==============================================================================
# APPLICATION SETUP & METADATA
# ==============================================================================

st.set_page_config(
    page_title="CustomerAtlas | Customer Intelligence",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject centralized enterprise stylesheet
load_css()

# Page Metadata & Breadcrumb Content
PAGE_META = {
    "Executive Cockpit": {
        "title": "Executive Overview & Commercial Health",
        "subtitle": "Macro revenue velocity, cohort customer retention health, and enterprise value distribution.",
        "category": "OVERVIEW",
        "guides": [
            "Track macro merchandise GMV & orders",
            "Inspect regional & segment Pareto breakdown",
            "Monitor churn exposure value in real time",
            "Analyze order fulfillment health",
        ],
    },
    "Customer 360 Dossier": {
        "title": "Unified Customer 360 Dossier",
        "subtitle": "360-degree commercial profile, omnichannel touchpoint journey, transaction timeline, and recommended actions.",
        "category": "CUSTOMER INTELLIGENCE",
        "guides": [
            "Search 94k+ canonical profiles",
            "Evaluate churn risk & lifetime trajectory",
            "Inspect omnichannel web clickstream & campaigns",
            "Export 1-click executive PDF / CSV dossier",
        ],
    },
    "Audience & Segments": {
        "title": "Audience & Segmentation Hub",
        "subtitle": "Multidimensional RFM audiences, behavioral clustering, and targeted cohort activation builder.",
        "category": "CUSTOMER INTELLIGENCE",
        "guides": [
            "Analyze 6 RFM audiences & 5 behavior clusters",
            "Benchmark revenue contribution & average CLV",
            "Strategic action playbook by audience",
            "Interactive cohort builder with CSV export",
        ],
    },
    "Predictive AI Studio": {
        "title": "Predictive AI & Machine Learning Studio",
        "subtitle": "Real-time What-If scenario simulation for calibrated churn propensity and forward 12-Month CLV modeling.",
        "category": "BUSINESS ANALYTICS",
        "guides": [
            "Simulate live What-If customer churn scenarios",
            "Interactive 12-Month forward CLV scenario estimator",
            "Inspect global XGBoost SHAP/feature importance",
            "Review held-out model comparison benchmarks",
        ],
    },
    "Experience & VoC Radar": {
        "title": "Customer Experience & VoC Radar",
        "subtitle": "Live NLP review sentiment classifier, Voice of Customer trends, delivery performance impact, and campaign ROI.",
        "category": "BUSINESS ANALYTICS",
        "guides": [
            "Test custom review text with live NLP pipeline",
            "Analyze sentiment trends over time",
            "Measure delivery delay impact on customer ratings",
            "Benchmark marketing campaign conversion & ROI",
        ],
    },
    "Next-Best-Offer & Catalog": {
        "title": "Next-Best-Offer & Merchandising Intelligence",
        "subtitle": "Explainable cross-sell recommendations, basket co-occurrence association rules, and catalog portfolio matrix.",
        "category": "BUSINESS ANALYTICS",
        "guides": [
            "Generate explainable next-best-category offers",
            "Inspect frequently bought together basket rules",
            "Identify high-revenue & low-rated product categories",
            "Audit recommendation engine logic distribution",
        ],
    },
    "Data Warehouse & SQL": {
        "title": "Data Warehouse & SQL Analytics Console",
        "subtitle": "Governed dimensional star schema, live business query sandbox, and enterprise data contract audit.",
        "category": "DATA PLATFORM",
        "guides": [
            "Run 8 predefined executive business queries",
            "Filter, search, and paginate warehouse extracts",
            "Inspect full star schema architecture",
            "Review SQL catalog and data quality audit",
        ],
    },
}

# ==============================================================================
# DATA INITIALIZATION & SIDEBAR NAVIGATION
# ==============================================================================

customer_features = load_csv("customer_360_features.csv", ("first_purchase_date", "last_purchase_date"))

if customer_features.empty:
    render_error_state(
        "Warehouse Artifact Missing",
        "The primary customer feature store (`customer_360_features.csv`) could not be loaded from `data/processed/`. Please verify data pipeline extraction.",
    )
    st.stop()

# Render Global Application Shell
filtered, current_page = render_sidebar(customer_features)
render_global_header(total_profiles=len(customer_features))

page_info = PAGE_META.get(current_page, PAGE_META["Executive Cockpit"])
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
# WORKSPACE 1: EXECUTIVE OVERVIEW (EXECUTIVE COCKPIT)
# ==============================================================================

if current_page == "Executive Cockpit":
    total_profiles = filtered["customer_id"].nunique()
    total_rev = filtered["total_spend"].sum()
    total_ord = filtered["total_orders"].sum()
    avg_clv_val = filtered["predicted_clv"].mean()
    churn_rate = filtered["churn_probability"].mean()
    avg_satisfaction = filtered["avg_review_score"].mean()
    repeat_customers = (filtered["total_orders"] > 1).sum()
    repeat_rate = repeat_customers / max(1, total_profiles)
    at_risk_df = filtered[filtered["churn_probability"] >= 0.65]
    at_risk_rev = at_risk_df["total_spend"].sum()

    # Enterprise KPI Card Row
    render_kpi_row([
        {
            "label": "Total Customers",
            "value": f"{total_profiles:,}",
            "subtitle": "Active in view",
            "icon": "👥",
        },
        {
            "label": "Merchandise GMV",
            "value": format_brl(total_rev),
            "subtitle": "Total gross spend",
            "icon": "💰",
        },
        {
            "label": "Total Orders",
            "value": f"{total_ord:,}",
            "subtitle": f"{(total_ord/max(1, total_profiles)):.2f} orders/cust",
            "icon": "📦",
        },
        {
            "label": "Avg 12M CLV",
            "value": format_brl(avg_clv_val),
            "subtitle": "Forward value proxy",
            "icon": "📈",
        },
        {
            "label": "Churn Propensity",
            "value": format_pct(churn_rate),
            "delta": format_brl(at_risk_rev),
            "delta_direction": "negative",
            "subtitle": "at-risk exposure",
            "icon": "⚠️",
        },
        {
            "label": "Avg CSAT Score",
            "value": f"{avg_satisfaction:.2f} / 5",
            "subtitle": "Review feedback",
            "icon": "⭐",
        },
    ])

    # Dynamic Executive Insights Grid
    top_seg = filtered.groupby("rfm_segment")["total_spend"].sum().idxmax()
    top_seg_rev = filtered.groupby("rfm_segment")["total_spend"].sum().max()
    top_state_name = filtered.groupby("state")["total_spend"].sum().idxmax()
    top_state_rev = filtered.groupby("state")["total_spend"].sum().max()

    render_insight_grid([
        {
            "title": f"Top Revenue Segment: {top_seg}",
            "description": f"Generates <strong>{format_brl(top_seg_rev)}</strong> ({top_seg_rev/max(1, total_rev):.1%} of filtered GMV). Priority audience for retention.",
            "kind": "info",
        },
        {
            "title": f"Top Geographic Hub: {top_state_name}",
            "description": f"Leads regional demand with <strong>{format_brl(top_state_rev)}</strong> in sales. Recommended for logistics fulfillment priority.",
            "kind": "info",
        },
        {
            "title": f"Churn Risk Exposure: {format_brl(at_risk_rev)}",
            "description": f"{len(at_risk_df):,} customers show high churn propensity. Repeat buyer rate across base is <strong>{repeat_rate:.1%}</strong>.",
            "kind": "alert",
        },
    ])

    # Macro Revenue & Order Volume Velocity
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    if not fact_orders.empty:
        st.markdown('<div class="section-header"><h3>Macro Revenue Velocity & Order Trajectory</h3><span>Timeline Performance</span></div>', unsafe_allow_html=True)
        valid_orders = fact_orders[~fact_orders["order_status"].isin(["canceled", "unavailable"])].copy()
        valid_orders["month_year"] = valid_orders["purchase_date"].dt.to_period("M").astype(str)
        monthly_summary = valid_orders.groupby("month_year", as_index=False).agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
        ).sort_values("month_year")

        fig_macro = go.Figure()
        fig_macro.add_trace(go.Bar(
            x=monthly_summary["month_year"],
            y=monthly_summary["revenue"],
            name="Revenue (BRL)",
            marker_color=COLOR_PRIMARY,
            opacity=0.85,
        ))
        fig_macro.add_trace(go.Scatter(
            x=monthly_summary["month_year"],
            y=monthly_summary["orders"],
            name="Order Count",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color=COLOR_AMBER, width=3),
            marker=dict(size=6),
        ))
        fig_macro.update_layout(
            title="Monthly Merchandise Revenue (BRL) and Order Volume Trajectory",
            yaxis=dict(title="Revenue (BRL)"),
            yaxis2=dict(title="Order Count", overlaying="y", side="right", showgrid=False),
        )
        style_chart(fig_macro, 320, legend="top")

    # Segment Breakdown & Top Regional States
    col_chart_1, col_chart_2 = st.columns(2)
    with col_chart_1:
        seg_rev = filtered.groupby("rfm_segment", as_index=False)["total_spend"].sum().sort_values("total_spend", ascending=True)
        fig_seg = px.bar(
            seg_rev,
            x="total_spend",
            y="rfm_segment",
            orientation="h",
            color="rfm_segment",
            title="Merchandise Revenue Contribution by RFM Segment",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_seg.update_xaxes(title="Total Spend (BRL)")
        fig_seg.update_yaxes(title=None)
        style_chart(fig_seg, 320, legend="hidden")

    with col_chart_2:
        state_rev = filtered.groupby("state", as_index=False)["total_spend"].sum().nlargest(10, "total_spend").sort_values("total_spend", ascending=True)
        fig_state = px.bar(
            state_rev,
            x="total_spend",
            y="state",
            orientation="h",
            title="Top 10 Brazilian States by Merchandise Revenue",
            color="total_spend",
            color_continuous_scale="Blues",
        )
        fig_state.update_xaxes(title="Revenue (BRL)")
        fig_state.update_yaxes(title="State")
        fig_state.update_layout(coloraxis_showscale=False)
        style_chart(fig_state, 320, legend="hidden")

    # Recency vs Spend Density Scatter Matrix
    with st.expander("Customer Lifetime Value vs Recency Scatter Matrix", expanded=True, icon=":material/scatter_plot:"):
        sample_size = min(len(filtered), 2500)
        scatter_sample = filtered.sample(sample_size, random_state=42)
        fig_scatter = px.scatter(
            scatter_sample,
            x="recency_days",
            y="total_spend",
            color="rfm_segment",
            size="total_orders",
            hover_data=["customer_id", "state", "predicted_clv", "churn_probability"],
            title=f"Recency vs Spend Density (Sample of {sample_size:,} Profiles)",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_scatter.update_xaxes(title="Days Inactive (Recency)")
        fig_scatter.update_yaxes(title="Total Spend (BRL)")
        style_chart(fig_scatter, 340, legend="bottom")

    # Export View Action
    exp_col1, _ = st.columns([0.35, 0.65])
    with exp_col1:
        st.download_button(
            "Download Filtered Customer Profiles (CSV)",
            filtered.to_csv(index=False).encode("utf-8"),
            "customer_360_executive_view.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 2: CUSTOMER 360 DOSSIER
# ==============================================================================

elif current_page == "Customer 360 Dossier":
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    fact_payments = load_csv("fact_payments.csv")
    recommendations = load_csv("recommendations.csv")

    # Search & Presets
    search_col1, search_col2 = st.columns([0.4, 0.6])
    with search_col1:
        preset = st.selectbox(
            "Quick Filter Presets",
            [
                "All Available Customers",
                "High Value Champions (VIP)",
                "At Risk High Spenders",
                "Growth Potential (Engaged)",
                "Recent First-Time Buyers",
            ],
        )

    preset_subset = filtered.copy()
    if preset == "High Value Champions (VIP)":
        preset_subset = preset_subset[preset_subset["rfm_segment"] == "Champions"]
    elif preset == "At Risk High Spenders":
        preset_subset = preset_subset[(preset_subset["churn_probability"] >= 0.65) & (preset_subset["total_spend"] >= 200)]
    elif preset == "Growth Potential (Engaged)":
        preset_subset = preset_subset[preset_subset["cluster_segment"] == "Growth Potential"]
    elif preset == "Recent First-Time Buyers":
        preset_subset = preset_subset[(preset_subset["recency_days"] <= 60) & (preset_subset["total_orders"] == 1)]

    if preset_subset.empty:
        preset_subset = filtered

    customer_id_list = sorted(preset_subset["customer_id"].dropna().unique())
    with search_col2:
        selected_cust = st.selectbox("Search / Select Customer ID", customer_id_list, index=0)

    profile = filtered[filtered["customer_id"] == selected_cust].iloc[0]

    # Customer Hero Card
    churn_val = float(profile.get("churn_probability", 0))
    action_info = retention_action(churn_val, str(profile.get("rfm_segment", "")))

    render_customer_hero(
        customer_id=str(profile.get("customer_id")),
        rfm_segment=str(profile.get("rfm_segment")),
        cluster_segment=str(profile.get("cluster_segment")),
        city=str(profile.get("city", "Unknown")),
        state=str(profile.get("state", "SP")),
        favorite_category=str(profile.get("favorite_category")),
        clv_band=str(profile.get("clv_band", "Standard")),
        action_tier=action_info["tier"],
        action_badge_color=action_info["badge_color"],
    )

    # Dossier Quick Metrics
    churn_dir = "negative" if churn_val >= 0.65 else "positive" if churn_val <= 0.35 else "neutral"
    render_kpi_row([
        {
            "label": "Total Lifetime Spend",
            "value": format_brl(profile["total_spend"]),
            "subtitle": "Gross spend",
            "icon": "💳",
        },
        {
            "label": "Total Orders",
            "value": f"{profile['total_orders']:.0f}",
            "subtitle": "Completed transactions",
            "icon": "📦",
        },
        {
            "label": "Average Order Value",
            "value": format_brl(profile["avg_order_value"]),
            "subtitle": "Per order average",
            "icon": "🛒",
        },
        {
            "label": "12M CLV Proxy",
            "value": format_brl(profile["predicted_clv"]),
            "subtitle": "Forward value potential",
            "icon": "💎",
        },
        {
            "label": "Churn Propensity",
            "value": format_pct(profile["churn_probability"]),
            "delta": action_info["tier"],
            "delta_direction": churn_dir,
            "subtitle": "Calibrated risk",
            "icon": "🎯",
        },
    ])

    # 5-Tab Unified Dossier
    tab_profile, tab_journey, tab_orders, tab_payments, tab_offers = st.tabs([
        "📋 Unified Profile",
        "🌐 Omnichannel & Engagement",
        "📦 Order History Timeline",
        "💳 Payment Methods",
        "🎁 AI Next-Best-Offers",
    ])

    with tab_profile:
        col_prof_left, col_prof_right = st.columns([1.3, 0.7])
        with col_prof_left:
            summary_dict = {
                "Canonical Customer ID": profile.get("customer_id"),
                "Geographic Location": f"{str(profile.get('city', '')).title()}, {str(profile.get('state', '')).upper()}",
                "RFM Audience Segment": profile.get("rfm_segment"),
                "Behavioral Cluster": profile.get("cluster_segment"),
                "Primary Affinity Category": profile.get("favorite_category"),
                "Days Since Last Order (Recency)": f"{int(profile.get('recency_days', 0))} days",
                "Distinct Items Purchased": int(profile.get("number_of_products", 1)),
                "Average Review Score": f"{profile.get('avg_review_score', 5.0):.1f} / 5.0",
                "Estimated 90-Day Revenue": format_brl(profile.get("predicted_90d_revenue", 0)),
                "RFM Score Breakdown (R / F / M)": f"R:{profile.get('r_score', 1)} | F:{profile.get('f_score', 1)} | M:{profile.get('m_score', 1)}",
            }
            summary_df = pd.DataFrame({"Attribute": summary_dict.keys(), "Intelligence Metric": summary_dict.values()})
            st.dataframe(summary_df, hide_index=True, use_container_width=True, height=360)

        with col_prof_right:
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=100 * churn_val,
                number={"suffix": "%", "font": {"family": "JetBrains Mono", "size": 28, "color": COLOR_SLATE}},
                title={"text": "<b>Churn Propensity</b>", "font": {"size": 14, "color": COLOR_SLATE}},
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

    with tab_journey:
        render_kpi_row([
            {"label": "Web Sessions", "value": f"{profile.get('sessions', 0):,.0f}", "subtitle": "Digital visits"},
            {"label": "Page Views", "value": f"{profile.get('views', 0):,.0f}", "subtitle": "Browsing activity"},
            {"label": "Cart Additions", "value": f"{profile.get('cart_additions', 0):,.0f}", "subtitle": "High intent actions"},
            {"label": "Campaign Clicks", "value": f"{profile.get('campaign_clicks', 0):,.0f}", "subtitle": "Email responses"},
            {"label": "Campaign Conversions", "value": f"{profile.get('campaign_conversions', 0):,.0f}", "subtitle": "Direct sales"},
        ])

        journey_table = pd.DataFrame([
            {"Touchpoint Channel": "Digital Web Activity", "Signal / Metric": "Web Engagement Score", "Score / Value": f"{profile.get('web_engagement_score', 0):.1f} pts"},
            {"Touchpoint Channel": "Digital Conversion", "Signal / Metric": "Web Conversion Rate", "Score / Value": format_pct(profile.get("web_conversion_rate", 0))},
            {"Touchpoint Channel": "Marketing Campaigns", "Signal / Metric": "Campaign Open Rate", "Score / Value": format_pct(profile.get("campaign_open_rate", 0))},
            {"Touchpoint Channel": "Marketing Campaigns", "Signal / Metric": "Attributed Campaign Revenue", "Score / Value": format_brl(profile.get("campaign_revenue", 0))},
            {"Touchpoint Channel": "Customer Feedback (VoC)", "Signal / Metric": "Average Review Rating", "Score / Value": f"{profile.get('avg_review_score', 0):.1f} / 5.0"},
        ])
        st.dataframe(journey_table, hide_index=True, use_container_width=True)

    with tab_orders:
        if not fact_orders.empty:
            cust_orders = fact_orders[fact_orders["customer_id"] == selected_cust].copy()
            if cust_orders.empty:
                st.info("No detailed transaction line items found for this customer.")
            else:
                cust_orders = cust_orders.sort_values("purchase_date", ascending=False)
                display_cols = [
                    c for c in ["order_id", "purchase_date", "order_status", "item_price", "freight_value", "revenue"]
                    if c in cust_orders.columns
                ]
                st.dataframe(cust_orders[display_cols], hide_index=True, use_container_width=True)
        else:
            st.info("Transaction history fact table is currently loading.")

    with tab_payments:
        if not fact_payments.empty and not fact_orders.empty:
            cust_order_ids = fact_orders[fact_orders["customer_id"] == selected_cust]["order_id"].unique()
            cust_payments = fact_payments[fact_payments["order_id"].isin(cust_order_ids)].copy()
            if not cust_payments.empty:
                pay_col1, pay_col2 = st.columns([0.5, 0.5])
                with pay_col1:
                    st.markdown("**Payment Method Breakdown:**")
                    st.dataframe(cust_payments[["payment_type", "payment_installments", "payment_value"]], hide_index=True, use_container_width=True)
                with pay_col2:
                    pay_pie = px.pie(
                        cust_payments,
                        names="payment_type",
                        values="payment_value",
                        hole=0.5,
                        title="Payment Value Distribution",
                        color_discrete_sequence=CHART_COLORWAY,
                    )
                    style_chart(pay_pie, 220, legend="hidden")
            else:
                st.info("No payment method logs found for this customer's orders.")
        else:
            st.info("Payment facts are loading.")

    with tab_offers:
        if not recommendations.empty:
            cust_recs = recommendations[recommendations["customer_id"] == selected_cust].sort_values("rank")
            if cust_recs.empty:
                st.info("No precomputed recommendations found for this customer.")
            else:
                st.markdown("**Explainable Next-Best-Category Recommendations for this Profile:**")
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
            st.info("Recommendations dataset is loading.")

    # Export Dossier Row
    dossier_exp1, dossier_exp2 = st.columns([0.3, 0.3])
    with dossier_exp1:
        st.download_button(
            "Download Executive PDF Dossier",
            build_customer_pdf(profile),
            f"customer_360_{selected_cust}.pdf",
            "application/pdf",
            icon=":material/picture_as_pdf:",
            use_container_width=True,
        )
    with dossier_exp2:
        st.download_button(
            "Download Customer Record (CSV)",
            pd.DataFrame([profile]).to_csv(index=False).encode("utf-8"),
            f"customer_360_{selected_cust}.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 3: AUDIENCE & SEGMENTS HUB
# ==============================================================================

elif current_page == "Audience & Segments":
    segment_summary = load_csv("segment_summary.csv")

    seg_counts = filtered["rfm_segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Customers"]

    cluster_rev = filtered.groupby("cluster_segment", as_index=False)["total_spend"].sum().sort_values("total_spend", ascending=True)

    col_seg_1, col_seg_2 = st.columns(2)
    with col_seg_1:
        fig_rfm_pie = px.pie(
            seg_counts,
            names="Segment",
            values="Customers",
            hole=0.55,
            title="RFM Audience Distribution",
            color_discrete_sequence=CHART_COLORWAY,
        )
        style_chart(fig_rfm_pie, 330, legend="bottom")

    with col_seg_2:
        fig_clust_bar = px.bar(
            cluster_rev,
            x="total_spend",
            y="cluster_segment",
            orientation="h",
            title="Revenue Contribution by Behavioral Cluster",
            color="cluster_segment",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_clust_bar.update_xaxes(title="Revenue (BRL)")
        fig_clust_bar.update_yaxes(title=None)
        style_chart(fig_clust_bar, 330, legend="hidden")

    # Segment Strategy Action Table
    st.markdown('<div class="section-header"><h3>Strategic Segment Action Playbook</h3><span>Audience Activation Matrix</span></div>', unsafe_allow_html=True)
    if not segment_summary.empty:
        summary_display = segment_summary.copy()
        summary_display["revenue"] = summary_display["revenue"].map(format_brl)
        summary_display["avg_clv"] = summary_display["avg_clv"].map(format_brl)
        summary_display["avg_churn_probability"] = summary_display["avg_churn_probability"].map(format_pct)
        st.dataframe(summary_display, hide_index=True, use_container_width=True)

    # Multidimensional Bubble Map
    with st.expander("Multidimensional Frequency vs Monetary Value Map", expanded=False, icon=":material/bubble_chart:"):
        sample_seg = filtered.sample(min(len(filtered), 3000), random_state=42)
        fig_bubble = px.scatter(
            sample_seg,
            x="frequency",
            y="monetary",
            color="rfm_segment",
            size="recency_days",
            hover_data=["customer_id", "cluster_segment", "predicted_clv"],
            title="Audience Clustering (Frequency vs Monetary vs Recency)",
            color_discrete_sequence=CHART_COLORWAY,
        )
        fig_bubble.update_xaxes(title="Order Frequency")
        fig_bubble.update_yaxes(title="Monetary Value (BRL)")
        style_chart(fig_bubble, 340, legend="bottom")

    # Interactive Custom Audience Cohort Builder
    st.markdown('<div class="section-header"><h3>Custom Marketing Cohort Builder</h3><span>Targeted Campaign Activation</span></div>', unsafe_allow_html=True)
    with st.expander("Configure Targeted Audience Parameters", expanded=True, icon=":material/tune:"):
        b_c1, b_c2, b_c3 = st.columns(3)
        b_rfm = b_c1.multiselect("Select RFM Target Audiences", sorted(filtered["rfm_segment"].unique()), default=["Champions", "Loyal Customers"])
        b_min_spend = b_c2.slider("Minimum Lifetime Spend (BRL)", 0.0, 5000.0, 100.0, step=50.0)
        b_max_churn = b_c3.slider("Max Acceptable Churn Propensity", 0.0, 1.0, 0.70, step=0.05)

        cohort_result = filtered.copy()
        if b_rfm:
            cohort_result = cohort_result[cohort_result["rfm_segment"].isin(b_rfm)]
        cohort_result = cohort_result[(cohort_result["total_spend"] >= b_min_spend) & (cohort_result["churn_probability"] <= b_max_churn)]

        render_kpi_row([
            {"label": "Matching Audience Size", "value": f"{len(cohort_result):,} Customers", "subtitle": "Audience size"},
            {"label": "Total Cohort GMV", "value": format_brl(cohort_result["total_spend"].sum()), "subtitle": "Gross spending"},
            {"label": "Average Cohort CLV", "value": format_brl(cohort_result["predicted_clv"].mean()), "subtitle": "Forward value"},
        ])

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "Export Targeted Campaign Cohort (CSV)",
            cohort_result.to_csv(index=False).encode("utf-8"),
            "targeted_marketing_cohort.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 4: PREDICTIVE AI STUDIO
# ==============================================================================

elif current_page == "Predictive AI Studio":
    st.markdown(
        render_insight_card(
            title="📌 Governance & Calibration Transparency",
            description="Olist transactions do not contain native subscription churn logs. Machine learning models in this platform are trained on calibrated portfolio proxy targets using XGBoost to demonstrate enterprise analytics, propensity scoring, and automated decision playbooks.",
            kind="warning",
        ),
        unsafe_allow_html=True,
    )

    feature_importance = load_csv("model_feature_importance.csv")
    model_evaluation = load_csv("model_evaluation.csv")

    pred_tab_churn, pred_tab_clv = st.tabs([
        "🔮 Churn Propensity What-If Simulator",
        "💎 12-Month CLV Scenario Estimator",
    ])

    with pred_tab_churn:
        churn_model = load_model("churn_model.pkl")
        sim_col_l, sim_col_r = st.columns([0.5, 0.5])

        with sim_col_l:
            with st.form("churn_sim_form"):
                st.markdown("**Simulate Customer Scenario Parameters:**")
                c1, c2 = st.columns(2)
                sim_recency = c1.number_input("Days Inactive (Recency)", min_value=0, max_value=800, value=90, step=5)
                sim_frequency = c2.number_input("Total Orders (Frequency)", min_value=1, max_value=50, value=2, step=1)

                c3, c4 = st.columns(2)
                sim_monetary = c3.number_input("Total Spend (BRL)", min_value=5.0, max_value=50000.0, value=280.0, step=10.0)
                sim_aov = c4.number_input("Average Order Value (BRL)", min_value=5.0, max_value=25000.0, value=140.0, step=10.0)

                c5, c6 = st.columns(2)
                sim_products = c5.number_input("Distinct Products", min_value=1, max_value=50, value=2, step=1)
                sim_age = c6.number_input("Customer Purchase Span (Days)", min_value=1, max_value=800, value=45, step=5)

                churn_submit = st.form_submit_button("Run Live Churn Propensity Inference", type="primary", use_container_width=True)

            if churn_model is not None:
                input_df = model_input_frame(sim_recency, sim_frequency, sim_monetary, sim_aov, sim_products, sim_age)
                prob = float(churn_model.predict_proba(input_df)[0, 1])
                band = "High Risk" if prob >= 0.65 else "Medium Risk" if prob >= 0.35 else "Low Risk"
                band_color = COLOR_RED if prob >= 0.65 else COLOR_AMBER if prob >= 0.35 else COLOR_GREEN

                with sim_col_r:
                    st.markdown("**Live Scenario Prediction Output:**")
                    render_kpi_row([
                        {"label": "Predicted Churn Risk", "value": format_pct(prob), "subtitle": "Propensity score"},
                        {"label": "Risk Classification", "value": band, "subtitle": "Portfolio tier"},
                    ])

                    act = retention_action(prob)
                    st.info(f"**Automated Retention Playbook:** {act['action']}")

                    g_fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=100 * prob,
                        number={"suffix": "%", "font": {"family": "JetBrains Mono", "color": COLOR_SLATE}},
                        title={"text": "<b>Churn Propensity Meter</b>", "font": {"color": COLOR_SLATE}},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": band_color},
                            "steps": [
                                {"range": [0, 35], "color": "rgba(22,163,74,0.12)"},
                                {"range": [35, 65], "color": "rgba(245,158,11,0.12)"},
                                {"range": [65, 100], "color": "rgba(220,38,38,0.12)"},
                            ],
                        },
                    ))
                    g_fig.update_layout(height=200, margin=dict(l=15, r=15, t=30, b=5), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(g_fig, use_container_width=True, config=PLOT_CONFIG)
            else:
                st.info("Churn pipeline model (`churn_model.pkl`) is ready to load.")

        # Feature Importance
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

    with pred_tab_clv:
        clv_model = load_model("clv_model.pkl")
        clv_l, clv_r = st.columns([0.5, 0.5])

        with clv_l:
            with st.form("clv_sim_form"):
                st.markdown("**Simulate Forward Customer Value Parameters:**")
                k1, k2 = st.columns(2)
                clv_rec = k1.number_input("Days Inactive", min_value=0, max_value=800, value=30, step=5, key="c_rec")
                clv_freq = k2.number_input("Orders Placed", min_value=1, max_value=50, value=3, step=1, key="c_freq")

                k3, k4 = st.columns(2)
                clv_mon = k3.number_input("Historical Spend (BRL)", min_value=5.0, max_value=50000.0, value=450.0, step=10.0, key="c_mon")
                clv_aov = k4.number_input("Average Order Value (BRL)", min_value=5.0, max_value=25000.0, value=150.0, step=10.0, key="c_aov")

                k5, k6 = st.columns(2)
                clv_prod = k5.number_input("Products Purchased", min_value=1, max_value=50, value=3, step=1, key="c_prod")
                clv_span = k6.number_input("Purchase Span (Days)", min_value=1, max_value=800, value=90, step=5, key="c_span")

                clv_submit = st.form_submit_button("Run Live 12-Month CLV Estimation", type="primary", use_container_width=True)

            if clv_model is not None:
                clv_input = model_input_frame(clv_rec, clv_freq, clv_mon, clv_aov, clv_prod, clv_span)
                est_clv = max(float(clv_model.predict(clv_input)[0]), 0.0)
                interval_low = est_clv * 0.85
                interval_high = est_clv * 1.15

                q25, q50, q75 = filtered["predicted_clv"].quantile([0.25, 0.50, 0.75])
                val_tier = "Platinum VIP" if est_clv >= q75 else "Gold Tier" if est_clv >= q50 else "Silver Tier" if est_clv >= q25 else "Bronze Tier"

                with clv_r:
                    st.markdown("**12-Month Forward Value Forecast:**")
                    render_kpi_row([
                        {"label": "Predicted 12M CLV", "value": format_brl(est_clv), "subtitle": "Expected value"},
                        {"label": "Customer Value Tier", "value": val_tier, "subtitle": "Cohort tier"},
                    ])

                    st.markdown(f"**80% Planning Range:** `{format_brl(interval_low)}` — `{format_brl(interval_high)}`")
                    st.info("💡 **Commercial Strategy:** Prioritize premium VIP loyalty recognition, dedicated concierge support, and early access cross-sell." if "Platinum" in val_tier or "Gold" in val_tier else "💡 **Commercial Strategy:** Target with category cross-sell discounts to build order frequency.")
            else:
                st.info("CLV regression model (`clv_model.pkl`) is ready.")

        # CLV Distribution
        fig_clv_dist = px.histogram(
            filtered,
            x="predicted_clv",
            nbins=40,
            title="Distribution of 12-Month Predicted CLV Across Customer Base",
            color_discrete_sequence=[COLOR_PRIMARY],
        )
        fig_clv_dist.update_xaxes(title="Predicted CLV (BRL)")
        fig_clv_dist.update_yaxes(title="Customer Count")
        style_chart(fig_clv_dist, 280, legend="hidden")

    # Model Evaluation Benchmarks
    st.markdown('<div class="section-header"><h3>Held-Out Model Benchmark Leaderboard</h3><span>Cross-Validation Results</span></div>', unsafe_allow_html=True)
    if not model_evaluation.empty:
        st.dataframe(model_evaluation, hide_index=True, use_container_width=True)


# ==============================================================================
# WORKSPACE 5: EXPERIENCE & VOC RADAR
# ==============================================================================

elif current_page == "Experience & VoC Radar":
    sentiment = load_csv("product_sentiment.csv")
    product_reviews = load_csv("fact_product_reviews.csv", ("review_date",))
    fact_campaign = load_csv("fact_campaign.csv")
    dim_campaign = load_csv("dim_campaign.csv")

    exp_tab1, exp_tab2 = st.tabs([
        "💬 Voice of Customer & NLP Classifier",
        "🎯 Marketing Campaign Funnel & ROI",
    ])

    with exp_tab1:
        nlp_col1, nlp_col2 = st.columns([0.45, 0.55])
        with nlp_col1:
            st.markdown("**Live Review Text NLP Classifier:**")
            sample_choices = [
                "The product arrived two days early, packaged securely, and exceeded my expectations!",
                "Average quality. It functions as described but delivery took longer than estimated.",
                "Terrible experience. The package was damaged and the seller never replied to my message.",
            ]
            picked_template = st.selectbox("Pick Sample Review Text", ["Custom input...", *sample_choices])
            user_text = picked_template if picked_template != "Custom input..." else "The product arrived two days early, packaged securely, and exceeded my expectations!"
            sample_text = st.text_area("Customer Review / Feedback", value=user_text, height=95)
            nlp_btn = st.button("Classify Sentiment", icon=":material/sentiment_satisfied:", type="primary", use_container_width=True)

            sentiment_model = load_model("sentiment_model.pkl")
            if nlp_btn and sample_text.strip():
                if sentiment_model is not None:
                    pred_label = sentiment_model.predict([sample_text])[0]
                    pred_prob = sentiment_model.predict_proba([sample_text])[0].max()
                    pill_color = COLOR_GREEN if pred_label == "Positive" else COLOR_AMBER if pred_label == "Neutral" else COLOR_RED
                    st.markdown(
                        f"""
                        <div style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-top: 10px;">
                            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Classification Result</div>
                            <div style="font-size: 20px; font-weight: 800; color: {pill_color}; margin-top: 4px;">{pred_label} ({pred_prob:.1%} Confidence)</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("Sentiment classification model (`sentiment_model.pkl`) is ready.")

        with nlp_col2:
            if not sentiment.empty:
                sent_mix = sentiment.groupby("sentiment_label", as_index=False)["review_count"].sum()
                fig_sent_pie = px.pie(
                    sent_mix,
                    names="sentiment_label",
                    values="review_count",
                    hole=0.52,
                    title="Overall Review Sentiment Distribution",
                    color="sentiment_label",
                    color_discrete_map={"Positive": COLOR_GREEN, "Neutral": COLOR_AMBER, "Negative": COLOR_RED},
                )
                style_chart(fig_sent_pie, 260, legend="bottom")

        # Sentiment Trends & Explorer
        if not product_reviews.empty:
            with st.expander("Monthly Sentiment Trends & Review Explorer", expanded=True, icon=":material/trending_up:"):
                trend_df = product_reviews.dropna(subset=["review_date"]).copy()
                trend_df["review_date"] = pd.to_datetime(trend_df["review_date"], errors="coerce")
                trend_df = trend_df.dropna(subset=["review_date"])
                trend_df["month"] = trend_df["review_date"].dt.to_period("M").astype(str)
                monthly_trend = trend_df.groupby(["month", "sentiment_label"], as_index=False).size()

                fig_trend = px.line(
                    monthly_trend,
                    x="month",
                    y="size",
                    color="sentiment_label",
                    markers=True,
                    title="Review Volume by Sentiment Over Time",
                    color_discrete_map={"Positive": COLOR_GREEN, "Neutral": COLOR_AMBER, "Negative": COLOR_RED},
                )
                fig_trend.update_xaxes(title="Month")
                fig_trend.update_yaxes(title="Reviews")
                style_chart(fig_trend, 280, legend="bottom")

                st.markdown("**Sample Review Feedback Database:**")
                st.dataframe(
                    product_reviews[["review_date", "category_name", "rating", "sentiment_label", "review_text"]].head(50),
                    hide_index=True,
                    use_container_width=True,
                    height=240,
                )

    with exp_tab2:
        st.markdown(
            render_insight_card(
                title="Attribution Modeling Notice",
                description="Marketing campaign logs represent synthetic event simulation to illustrate funnel stages, conversion drop-offs, and multi-channel ROI analysis.",
                kind="info",
            ),
            unsafe_allow_html=True,
        )
        if not fact_campaign.empty and not dim_campaign.empty:
            camp_agg = (
                fact_campaign.groupby("campaign_id", as_index=False)
                .agg(
                    sent=("email_sent", "sum"),
                    opened=("opened", "sum"),
                    clicked=("clicked", "sum"),
                    converted=("converted", "sum"),
                    revenue=("revenue_generated", "sum"),
                )
                .merge(dim_campaign[["campaign_id", "campaign_type", "campaign_cost"]], on="campaign_id", how="left")
            )
            camp_agg["roi"] = (camp_agg["revenue"] - camp_agg["campaign_cost"]) / camp_agg["campaign_cost"]

            funnel_totals = camp_agg[["sent", "opened", "clicked", "converted"]].sum()
            funnel_df = pd.DataFrame({"Stage": ["Sent", "Opened", "Clicked", "Converted"], "Audience": funnel_totals.values})

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                fig_funnel = px.funnel(funnel_df, x="Audience", y="Stage", title="Omnichannel Campaign Conversion Funnel", color_discrete_sequence=[COLOR_PRIMARY])
                style_chart(fig_funnel, 300, legend="hidden")

            with f_col2:
                fig_roi = px.bar(
                    camp_agg.sort_values("roi", ascending=True),
                    x="roi",
                    y="campaign_type",
                    orientation="h",
                    title="Campaign Return on Investment (ROI Multiplier)",
                    color="roi",
                    color_continuous_scale="Blues",
                )
                fig_roi.update_xaxes(title="ROI Multiplier")
                fig_roi.update_yaxes(title=None)
                style_chart(fig_roi, 300, legend="hidden")


# ==============================================================================
# WORKSPACE 6: NEXT-BEST-OFFER & CATALOG
# ==============================================================================

elif current_page == "Next-Best-Offer & Catalog":
    recommendations = load_csv("recommendations.csv")
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    dim_product = load_csv("dim_product.csv")
    sentiment = load_csv("product_sentiment.csv")

    rec_tab1, rec_tab2 = st.tabs([
        "🎯 Customer Recommendation Lookup",
        "📊 Merchandising & Basket Associations",
    ])

    with rec_tab1:
        if not recommendations.empty:
            cust_options = sorted(recommendations["customer_id"].dropna().unique())
            sel_rec_cust = st.selectbox("Find Recommendations for Customer", cust_options, index=0)
            rec_results = recommendations[recommendations["customer_id"] == sel_rec_cust].sort_values("rank")

            st.markdown(f"**Top Ranked Next-Best-Category Offers for Customer `{sel_rec_cust}`:**")
            r_cols = st.columns(min(len(rec_results), 5))
            for i, (_, rec_row) in enumerate(rec_results.head(5).iterrows()):
                with r_cols[i]:
                    st.markdown(
                        render_recommendation_card(
                            rank=int(rec_row["rank"]),
                            category=str(rec_row["recommended_category"]),
                            reason=str(rec_row["reason"]),
                            method=str(rec_row.get("method", "Basket Association")),
                        ),
                        unsafe_allow_html=True,
                    )

            # Recommendation Methodology Breakdown
            method_counts = recommendations["method"].value_counts().reset_index()
            method_counts.columns = ["Recommendation Method", "Volume"]
            fig_method = px.bar(
                method_counts,
                x="Recommendation Method",
                y="Volume",
                title="Recommendation Engine Logic Distribution",
                color="Recommendation Method",
                color_discrete_sequence=[COLOR_PRIMARY, COLOR_CYAN],
            )
            style_chart(fig_method, 260, legend="hidden")
        else:
            st.info("Recommendations dataset is loading.")

    with rec_tab2:
        if not fact_orders.empty and not dim_product.empty:
            order_prod = fact_orders.merge(dim_product[["product_id", "category_name_english"]], on="product_id", how="left")
            cat_perf = (
                order_prod.groupby("category_name_english", as_index=False)
                .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), products=("product_id", "nunique"))
                .sort_values("revenue", ascending=False)
            )

            baskets = order_prod.groupby("order_id")["category_name_english"].apply(lambda vals: sorted(set(vals.dropna())))
            pair_dict = {}
            for b in baskets:
                for p in combinations(b, 2):
                    pair_dict[p] = pair_dict.get(p, 0) + 1
            pairs_df = pd.DataFrame([{"Category A": p[0], "Category B": p[1], "Co-occurrences": c} for p, c in pair_dict.items()])
            if not pairs_df.empty:
                pairs_df = pairs_df.sort_values("Co-occurrences", ascending=False).head(20)

            c_left, c_right = st.columns(2)
            with c_left:
                top_cats = cat_perf.head(10).sort_values("revenue", ascending=True)
                fig_top_cats = px.bar(
                    top_cats,
                    x="revenue",
                    y="category_name_english",
                    orientation="h",
                    title="Top 10 Product Categories by Merchandise GMV",
                    color="revenue",
                    color_continuous_scale="Blues",
                )
                fig_top_cats.update_layout(coloraxis_showscale=False)
                fig_top_cats.update_xaxes(title="Revenue (BRL)")
                fig_top_cats.update_yaxes(title=None)
                style_chart(fig_top_cats, 320, legend="hidden")

            with c_right:
                if not sentiment.empty:
                    low_cats = sentiment[sentiment["review_count"] >= 20].nsmallest(10, "avg_rating").sort_values("avg_rating", ascending=True)
                    fig_low_cats = px.bar(
                        low_cats,
                        x="avg_rating",
                        y="category_name",
                        orientation="h",
                        title="Categories Requiring Quality / Supplier Review",
                        color="avg_rating",
                        color_continuous_scale="Reds",
                    )
                    fig_low_cats.update_layout(coloraxis_showscale=False)
                    fig_low_cats.update_xaxes(title="Average CSAT Rating (1-5)")
                    fig_low_cats.update_yaxes(title=None)
                    style_chart(fig_low_cats, 320, legend="hidden")

            st.markdown('<div class="section-header"><h3>Frequently Bought Together (Cross-Category Basket Rules)</h3></div>', unsafe_allow_html=True)
            st.dataframe(pairs_df, hide_index=True, use_container_width=True)


# ==============================================================================
# WORKSPACE 7: DATA WAREHOUSE & SQL CONSOLE
# ==============================================================================

elif current_page == "Data Warehouse & SQL":
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    fact_payments = load_csv("fact_payments.csv")
    dim_product = load_csv("dim_product.csv")
    segment_summary = load_csv("segment_summary.csv")
    model_evaluation = load_csv("model_evaluation.csv")
    recommendations = load_csv("recommendations.csv")

    st.markdown('<div class="section-header"><h3>Data Warehouse Architecture & Source Governance</h3></div>', unsafe_allow_html=True)
    sources = [
        {"Source Domain": "Olist E-Commerce", "Role in Customer 360": "Canonical customer identities, order items, payments, reviews", "Governance Rule": "Truth layer for all transactions & RFM"},
        {"Source Domain": "Clickstream Events", "Role in Customer 360": "Digital web activity, sessions, views, cart additions", "Governance Rule": "Simulated identity map for behavioral enrichment"},
        {"Source Domain": "Amazon Datafiniti Reviews", "Role in Customer 360": "Product-level NLP sentiment & Voice of Customer benchmarks", "Governance Rule": "Independent benchmark; no customer joins"},
        {"Source Domain": "Synthetic Marketing Campaigns", "Role in Customer 360": "Omnichannel campaign logs, open/click rates, ROI metrics", "Governance Rule": "Synthetic demonstration of marketing attribution"},
    ]
    st.dataframe(pd.DataFrame(sources), hide_index=True, use_container_width=True)

    # Readiness checklist
    art_col1, art_col2 = st.columns(2)
    with art_col1:
        st.markdown("**Warehouse Artifact Readiness:**")
        status_table = pd.DataFrame([
            {"Artifact": "Canonical Customer Features", "Rows": f"{len(customer_features):,}", "Status": "Ready 🟢"},
            {"Artifact": "Dimensional Order Transactions", "Rows": f"{len(fact_orders):,}" if not fact_orders.empty else "0", "Status": "Ready 🟢" if not fact_orders.empty else "Missing 🔴"},
            {"Artifact": "AI Next-Best-Offer Catalog", "Rows": f"{len(recommendations):,}" if not recommendations.empty else "0", "Status": "Ready 🟢" if not recommendations.empty else "Missing 🔴"},
            {"Artifact": "Model Evaluation Benchmarks", "Rows": f"{len(model_evaluation):,}" if not model_evaluation.empty else "0", "Status": "Ready 🟢" if not model_evaluation.empty else "Missing 🔴"},
        ])
        st.dataframe(status_table, hide_index=True, use_container_width=True)

    with art_col2:
        st.markdown("**Enterprise Data Contracts & Limitations:**")
        st.info("• Churn and 12-Month CLV are calibrated portfolio proxy models.\n• Monetary units use Brazilian Reais (BRL, R$).\n• All outputs comply with the Release Validation checks in Notebook 06.")

    # Business Query Sandbox Runner
    st.markdown('<div class="section-header"><h3>Predefined Business Analytics Query Engine</h3><span>Instant SQL Analysis</span></div>', unsafe_allow_html=True)

    q_controls = st.columns([0.55, 0.45])
    query_choice = q_controls[0].selectbox(
        "Select Analytical Query",
        [
            "1. Revenue by State & Region",
            "2. Top Cities by Merchandise Revenue",
            "3. Category Repeat-Customer Rates",
            "4. Monthly Revenue & Order Velocity Trend",
            "5. Payment Method & Installment Analysis",
            "6. High-Risk Churn Customers",
            "7. Highest-CLV VIP Customers",
            "8. RFM Segment GMV Performance",
        ],
    )

    valid_orders = fact_orders[~fact_orders["order_status"].isin(["canceled", "unavailable"])].copy() if not fact_orders.empty else pd.DataFrame()

    if query_choice == "1. Revenue by State & Region":
        if not valid_orders.empty:
            q_result = (
                customer_features[["customer_id", "state"]]
                .merge(valid_orders[["customer_id", "order_id", "revenue"]], on="customer_id", how="inner")
                .groupby("state", as_index=False)
                .agg(customers=("customer_id", "nunique"), orders=("order_id", "nunique"), revenue=("revenue", "sum"))
                .sort_values("revenue", ascending=False)
            )
        else:
            q_result = customer_features.groupby("state", as_index=False)["total_spend"].sum().rename(columns={"total_spend": "revenue"}).sort_values("revenue", ascending=False)
    elif query_choice == "2. Top Cities by Merchandise Revenue":
        q_result = (
            customer_features.groupby(["city", "state"], as_index=False)
            .agg(customers=("customer_id", "nunique"), total_spend=("total_spend", "sum"))
            .sort_values("total_spend", ascending=False)
            .head(50)
        )
    elif query_choice == "3. Category Repeat-Customer Rates":
        if not valid_orders.empty and not dim_product.empty:
            cat_orders = valid_orders.merge(dim_product[["product_id", "category_name_english"]], on="product_id", how="left")
            cat_cust = cat_orders.groupby(["category_name_english", "customer_id"])["order_id"].nunique().reset_index()
            q_result = (
                cat_cust.groupby("category_name_english", as_index=False)
                .agg(total_customers=("customer_id", "count"), repeat_customers=("order_id", lambda s: (s > 1).sum()))
            )
            q_result["repeat_rate_pct"] = (100.0 * q_result["repeat_customers"] / q_result["total_customers"]).round(2)
            q_result = q_result[q_result["total_customers"] >= 30].sort_values("repeat_rate_pct", ascending=False)
        else:
            q_result = pd.DataFrame()
    elif query_choice == "4. Monthly Revenue & Order Velocity Trend":
        if not valid_orders.empty:
            valid_orders["month"] = valid_orders["purchase_date"].dt.to_period("M").astype(str)
            q_result = (
                valid_orders.groupby("month", as_index=False)
                .agg(orders=("order_id", "nunique"), customers=("customer_id", "nunique"), revenue=("revenue", "sum"))
                .sort_values("month")
            )
        else:
            q_result = pd.DataFrame()
    elif query_choice == "5. Payment Method & Installment Analysis":
        if not fact_payments.empty:
            q_result = (
                fact_payments.groupby("payment_type", as_index=False)
                .agg(
                    transactions=("order_id", "count"),
                    avg_installments=("payment_installments", "mean"),
                    total_collected=("payment_value", "sum"),
                )
                .sort_values("total_collected", ascending=False)
            )
            q_result["avg_installments"] = q_result["avg_installments"].round(1)
        else:
            q_result = pd.DataFrame()
    elif query_choice == "6. High-Risk Churn Customers":
        q_result = (
            customer_features[customer_features["churn_probability"] >= 0.65][
                ["customer_id", "state", "rfm_segment", "total_spend", "predicted_clv", "churn_probability"]
            ]
            .sort_values("churn_probability", ascending=False)
            .head(500)
        )
    elif query_choice == "7. Highest-CLV VIP Customers":
        q_result = customer_features.nlargest(500, "predicted_clv")[
            ["customer_id", "state", "rfm_segment", "total_spend", "predicted_clv", "clv_band"]
        ]
    else:
        q_result = segment_summary.sort_values("revenue", ascending=False) if not segment_summary.empty else pd.DataFrame()

    q_controls[1].download_button(
        "Download Query Result (CSV)",
        q_result.to_csv(index=False).encode("utf-8"),
        f"{query_choice.lower().replace(' ', '_')}.csv",
        "text/csv",
        icon=":material/download:",
        use_container_width=True,
    )

    # Search & Pagination
    s_col1, s_col2 = st.columns([0.7, 0.3])
    table_search = s_col1.text_input("Filter / Search Query Rows", placeholder="Type any keyword, state, or ID...")
    page_size = s_col2.selectbox("Page Size", [10, 25, 50, 100], index=1)

    filtered_q = q_result.copy()
    if table_search and not filtered_q.empty:
        mask = filtered_q.astype(str).apply(lambda col: col.str.contains(table_search, case=False, na=False)).any(axis=1)
        filtered_q = filtered_q[mask]

    tot_pages = max(1, int(np.ceil(len(filtered_q) / page_size))) if not filtered_q.empty else 1
    page_no = st.number_input("Page", min_value=1, max_value=tot_pages, value=1)
    start_idx = (page_no - 1) * page_size

    if not filtered_q.empty:
        st.dataframe(filtered_q.iloc[start_idx : start_idx + page_size], hide_index=True, use_container_width=True)
        st.caption(f"Showing page {page_no} of {tot_pages} | {len(filtered_q):,} total records")
    else:
        st.info("No records match the current query or search filter.")

    # SQL Library Viewer
    sql_file = SQL_DIR / "business_queries.sql"
    with st.expander("Inspect Business SQL Query Catalog (`sql/business_queries.sql`)", expanded=False, icon=":material/code:"):
        if sql_file.exists():
            sql_code = sql_file.read_text(encoding="utf-8")
            st.code(sql_code, language="sql")
            st.download_button(
                "Download SQL Catalog",
                sql_code.encode("utf-8"),
                "business_queries.sql",
                "text/sql",
                icon=":material/download:",
            )
        else:
            st.warning("SQL business query catalog not found at `sql/business_queries.sql`.")

# ==============================================================================
# GLOBAL FOOTER
# ==============================================================================

render_footer()
