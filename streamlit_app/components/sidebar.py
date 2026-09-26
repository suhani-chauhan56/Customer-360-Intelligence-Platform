"""Enterprise sidebar navigation and filter drawer components for CustomerAtlas.

Implements structured navigation hierarchy aligned with the 10 core Product Workspaces:
- OVERVIEW: Executive Overview
- CUSTOMER INTELLIGENCE: Customer 360, Customer Segmentation, Customer Value / CLV
- PREDICTIVE & RISK: Churn Intelligence, Sentiment Intelligence, Recommendations
- EXPLORATION & GOVERNANCE: Analytics Explorer, Data Quality, Methodology / About
- AI DECISION SUPPORT: Ask CustomerAtlas
"""

from typing import List, Tuple
import pandas as pd
import streamlit as st

# Enterprise Navigation Hierarchy
NAV_SECTIONS: List[Tuple[str, List[Tuple[str, str, str]]]] = [
    (
        "EXECUTIVE OVERVIEW",
        [
            ("Executive Overview", "Executive Overview", ":material/dashboard:"),
        ],
    ),
    (
        "CUSTOMER INTELLIGENCE",
        [
            ("Customer 360", "Customer 360", ":material/person_search:"),
            ("Customer Segmentation", "Customer Segmentation", ":material/pie_chart:"),
            ("Customer Value / CLV", "Customer Value / CLV", ":material/diamond:"),
        ],
    ),
    (
        "PREDICTIVE & RISK AI",
        [
            ("Churn Intelligence", "Churn Intelligence", ":material/warning:"),
            ("Sentiment Intelligence", "Sentiment Intelligence", ":material/reviews:"),
            ("Recommendations", "Recommendations", ":material/recommend:"),
        ],
    ),
    (
        "EXPLORATION & GOVERNANCE",
        [
            ("Analytics Explorer", "Analytics Explorer", ":material/manage_search:"),
            ("Data Quality", "Data Quality", ":material/verified_user:"),
            ("Methodology / About", "Methodology / About", ":material/menu_book:"),
        ],
    ),
    (
        "DECISION SUPPORT",
        [
            ("Ask CustomerAtlas", "Ask CustomerAtlas", ":material/psychology:"),
        ],
    ),
]


def render_sidebar(customer_features: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Render the enterprise sidebar with CustomerAtlas branding, navigation, and filters.

    Returns:
        Tuple of (filtered_dataframe, active_page_key)
    """
    with st.sidebar:
        # Sidebar Brand Header
        st.markdown(
            """
            <div class="sidebar-brand-container">
                <div class="sidebar-brand-icon">CA</div>
                <div>
                    <div class="sidebar-brand-title">CustomerAtlas AI</div>
                    <div class="sidebar-brand-subtitle">Unified Customer Intelligence</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation Groups
        current_page = st.session_state.get("active_page", "Executive Overview")

        for section_title, items in NAV_SECTIONS:
            st.markdown(f'<div class="nav-category-header">{section_title}</div>', unsafe_allow_html=True)
            for display_label, page_key, icon in items:
                is_active = (current_page == page_key)
                if st.button(
                    display_label,
                    key=f"nav_btn_{page_key}",
                    icon=icon,
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.active_page = page_key
                    st.rerun()

        # Global Audience Filters
        st.markdown('<div class="nav-category-header">GLOBAL AUDIENCE FILTERS</div>', unsafe_allow_html=True)
        with st.expander("Filter Customer Base", expanded=False, icon=":material/tune:"):
            min_date = customer_features["last_purchase_date"].min().date() if "last_purchase_date" in customer_features.columns and hasattr(customer_features["last_purchase_date"], "dt") else None
            max_date = customer_features["last_purchase_date"].max().date() if "last_purchase_date" in customer_features.columns and hasattr(customer_features["last_purchase_date"], "dt") else None

            if st.session_state.get("reset_filters_flag", False):
                st.session_state.global_rfm = "All"
                st.session_state.global_state = "All"
                st.session_state.global_risk = "All"
                st.session_state.global_cat = "All"
                if min_date and max_date:
                    st.session_state.global_date_range = (min_date, max_date)
                st.session_state.reset_filters_flag = False

            segment_options = ["All", *sorted(customer_features["rfm_segment"].dropna().unique())]
            selected_segment = st.selectbox("RFM Segment", segment_options, key="global_rfm")

            risk_options = ["All", "Low Risk (<35%)", "Medium Risk (35-65%)", "High Risk (>=65%)"]
            selected_risk = st.selectbox("Risk Level", risk_options, key="global_risk")

            state_options = ["All", *sorted(customer_features["state"].dropna().unique())]
            selected_state = st.selectbox("State / Region", state_options, key="global_state")

            cat_options = ["All", *sorted(customer_features["favorite_category"].dropna().unique())]
            selected_category = st.selectbox("Favorite Category", cat_options, key="global_cat")

            if min_date and max_date:
                date_range = st.date_input(
                    "Purchase Date Window",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="global_date_range",
                )
            else:
                date_range = None

            if st.button("Reset All Filters", icon=":material/restart_alt:", use_container_width=True):
                st.session_state.reset_filters_flag = True
                st.rerun()

        # System Metadata Footer
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        st.caption(f"Connected: **{len(customer_features):,} Profiles**")
        st.caption("Platform: **CustomerAtlas AI v2.5**")

    # Apply Filters to dataset
    filtered = customer_features.copy()
    if selected_segment != "All":
        filtered = filtered[filtered["rfm_segment"] == selected_segment]
    if selected_risk != "All" and "churn_probability" in filtered.columns:
        if selected_risk == "High Risk (>=65%)":
            filtered = filtered[filtered["churn_probability"] >= 0.65]
        elif selected_risk == "Medium Risk (35-65%)":
            filtered = filtered[(filtered["churn_probability"] >= 0.35) & (filtered["churn_probability"] < 0.65)]
        elif selected_risk == "Low Risk (<35%)":
            filtered = filtered[filtered["churn_probability"] < 0.35]
    if selected_state != "All" and "state" in filtered.columns:
        filtered = filtered[filtered["state"] == selected_state]
    if selected_category != "All":
        filtered = filtered[filtered["favorite_category"] == selected_category]
    if date_range and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        try:
            start_dt, end_dt = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
            if "last_purchase_date" in filtered.columns:
                filtered = filtered[filtered["last_purchase_date"].between(start_dt, end_dt)]
        except Exception:
            pass

    return filtered, st.session_state.get("active_page", "Executive Overview")
