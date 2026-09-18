"""Customer Table Presentation Component for CustomerAtlas.

Provides an enterprise analytical table with sorting, pagination, clean formatting,
risk badges, segment badges, and direct 1-click drill-down into Customer 360.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
import streamlit as st
from utils.formatting import format_brl, format_pct


def render_customer_table(
    df: pd.DataFrame,
    page_size_default: int = 25,
    key_prefix: str = "cust_tbl",
) -> None:
    """Render a paginated, decision-useful customer table with selection actions."""
    if df is None or df.empty:
        st.info("No matching customer records to display.")
        return

    # Table Controls Header
    c1, c2, c3 = st.columns([0.45, 0.35, 0.20])
    with c1:
        st.markdown(f"**Showing {len(df):,} matching customer profiles**")
    with c2:
        sort_by = st.selectbox(
            "Sort by",
            [
                "Total Spend (High to Low)",
                "Predicted 12M CLV (High to Low)",
                "Churn Risk (High to Low)",
                "Recency (Most Recent)",
                "Orders (Most Frequent)",
            ],
            key=f"{key_prefix}_sort",
        )
    with c3:
        page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1, key=f"{key_prefix}_ps")

    # Apply Sorting
    sorted_df = df.copy()
    if sort_by == "Total Spend (High to Low)":
        sorted_df = sorted_df.sort_values("total_spend", ascending=False)
    elif sort_by == "Predicted 12M CLV (High to Low)":
        sorted_df = sorted_df.sort_values("predicted_clv", ascending=False)
    elif sort_by == "Churn Risk (High to Low)":
        sorted_df = sorted_df.sort_values("churn_probability", ascending=False)
    elif sort_by == "Recency (Most Recent)":
        sorted_df = sorted_df.sort_values("recency_days", ascending=True)
    elif sort_by == "Orders (Most Frequent)":
        sorted_df = sorted_df.sort_values("total_orders", ascending=False)

    # Pagination Logic
    total_rows = len(sorted_df)
    total_pages = max(1, int(np.ceil(total_rows / page_size)))
    
    col_p1, col_p2 = st.columns([0.25, 0.75])
    with col_p1:
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key=f"{key_prefix}_pno")
    with col_p2:
        start_idx = (page_num - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        st.caption(f"Displaying rows {start_idx + 1:,} – {end_idx:,} of {total_rows:,} total records (Page {page_num} of {total_pages})")

    page_data = sorted_df.iloc[start_idx:end_idx].copy()

    # Format Display Columns
    display_df = pd.DataFrame()
    display_df["Customer ID"] = page_data["customer_id"].astype(str)
    display_df["Segment"] = page_data["rfm_segment"].astype(str)
    display_df["Location"] = page_data["city"].str.title() + ", " + page_data["state"].str.upper()
    display_df["Orders"] = page_data["total_orders"].astype(int)
    display_df["Total Spend"] = page_data["total_spend"].map(format_brl)
    display_df["AOV"] = page_data["avg_order_value"].map(format_brl)
    display_df["Recency"] = page_data["recency_days"].astype(int).astype(str) + " days"
    display_df["12M CLV"] = page_data["predicted_clv"].map(format_brl)
    display_df["Churn Risk"] = page_data["churn_probability"].map(format_pct)
    display_df["Value Band"] = page_data["clv_band"].astype(str)

    st.dataframe(display_df, hide_index=True, use_container_width=True)

    # 1-Click Customer Selection into Customer 360
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    sel_col1, sel_col2 = st.columns([0.65, 0.35])
    with sel_col1:
        cust_choices = page_data["customer_id"].tolist()
        picked_cust = st.selectbox(
            "Select a customer from this page to inspect in Customer 360:",
            cust_choices,
            format_func=lambda cid: f"Customer #{cid} — {page_data[page_data['customer_id'] == cid]['rfm_segment'].iloc[0]} ({format_brl(page_data[page_data['customer_id'] == cid]['total_spend'].iloc[0])})",
            key=f"{key_prefix}_select_cid",
        )
    with sel_col2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 View Customer 360 Profile", key=f"{key_prefix}_open_btn", type="primary", use_container_width=True):
            st.session_state.selected_customer_id = picked_cust
            st.session_state.active_page = "Customer 360"
            st.rerun()
