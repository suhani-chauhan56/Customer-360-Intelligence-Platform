"""Enterprise sidebar navigation and filter drawer components for CustomerAtlas.

Implements structured navigation hierarchy, active page state indicators,
and unified global audience filtering.
"""

from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

# Enterprise Navigation Hierarchy: Grouped by operational domain
NAV_SECTIONS: List[Tuple[str, List[Tuple[str, str, str]]]] = [
    (
        "OVERVIEW",
        [
            ("Executive Overview", "Executive Cockpit", ":material/dashboard:"),
        ],
    ),
    (
        "CUSTOMER INTELLIGENCE",
        [
            ("Customer 360 Dossier", "Customer 360 Dossier", ":material/person_search:"),
            ("Audience & Segments", "Audience & Segments", ":material/pie_chart:"),
        ],
    ),
    (
        "BUSINESS ANALYTICS",
        [
            ("Predictive AI Studio", "Predictive AI Studio", ":material/psychology:"),
            ("Experience & VoC Radar", "Experience & VoC Radar", ":material/forum:"),
            ("Next-Best-Offer & Catalog", "Next-Best-Offer & Catalog", ":material/auto_awesome:"),
        ],
    ),
    (
        "DATA PLATFORM",
        [
            ("Data Warehouse & SQL", "Data Warehouse & SQL", ":material/database:"),
        ],
    ),
]


def render_sidebar(customer_features: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Render the enterprise sidebar with CustomerAtlas branding, navigation, and filters.

    Returns:
        Tuple of (filtered_dataframe, active_page_key)
    """
    with st.sidebar:
        # Sidebar Brand
        st.markdown(
            """
            <div class="sidebar-brand-container">
                <div class="sidebar-brand-icon">CA</div>
                <div>
                    <div class="sidebar-brand-title">CustomerAtlas</div>
                    <div class="sidebar-brand-subtitle">Unified Customer Intelligence</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation Groups
        current_page = st.session_state.get("active_page", "Executive Cockpit")

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
        st.markdown('<div class="nav-category-header">GLOBAL FILTERS</div>', unsafe_allow_html=True)
        with st.expander("Filter Audience", expanded=False, icon=":material/tune:"):
            min_date = customer_features["last_purchase_date"].min().date()
            max_date = customer_features["last_purchase_date"].max().date()

            if st.session_state.get("reset_filters_flag", False):
                st.session_state.global_rfm = "All"
                st.session_state.global_state = "All"
                st.session_state.global_cat = "All"
                st.session_state.global_date_range = (min_date, max_date)
                st.session_state.reset_filters_flag = False

            segment_options = ["All", *sorted(customer_features["rfm_segment"].dropna().unique())]
            selected_segment = st.selectbox("RFM Segment", segment_options, key="global_rfm")

            state_options = ["All", *sorted(customer_features["state"].dropna().unique())]
            selected_state = st.selectbox("State / Region", state_options, key="global_state")

            cat_options = ["All", *sorted(customer_features["favorite_category"].dropna().unique())]
            selected_category = st.selectbox("Favorite Category", cat_options, key="global_cat")

            date_range = st.date_input(
                "Purchase Date Window",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="global_date_range",
            )

            if st.button("Reset Filters", icon=":material/restart_alt:", use_container_width=True):
                st.session_state.reset_filters_flag = True
                st.rerun()

        # System Metadata Footer
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        st.caption(f"Connected: **{len(customer_features):,} Profiles**")
        st.caption("Release: **v1.0 Production Base**")

    # Apply Filters to dataset
    filtered = customer_features.copy()
    if selected_segment != "All":
        filtered = filtered[filtered["rfm_segment"] == selected_segment]
    if selected_state != "All" and "state" in filtered.columns:
        filtered = filtered[filtered["state"] == selected_state]
    if selected_category != "All":
        filtered = filtered[filtered["favorite_category"] == selected_category]
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_dt, end_dt = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        filtered = filtered[filtered["last_purchase_date"].between(start_dt, end_dt)]

    return filtered, st.session_state.get("active_page", "Executive Cockpit")
