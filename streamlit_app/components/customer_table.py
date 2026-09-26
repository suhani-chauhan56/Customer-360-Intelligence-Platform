"""Customer Table Presentation Component for CustomerAtlas.

Provides an enterprise analytical table with sorting, pagination, clean formatting,
risk badges, segment badges, defensive column resolution, and direct 1-click drill-down into Customer 360.
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
    """Render a paginated, decision-useful customer table with selection actions.

    Defensively validates columns, computes missing derived metrics (such as AOV)
    on the fly if absent, and prevents runtime KeyError exceptions.
    """
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

    # Apply Sorting defensively
    sorted_df = df.copy()
    if sort_by == "Total Spend (High to Low)" and "total_spend" in sorted_df.columns:
        sorted_df = sorted_df.sort_values("total_spend", ascending=False)
    elif sort_by == "Predicted 12M CLV (High to Low)" and "predicted_clv" in sorted_df.columns:
        sorted_df = sorted_df.sort_values("predicted_clv", ascending=False)
    elif sort_by == "Churn Risk (High to Low)" and "churn_probability" in sorted_df.columns:
        sorted_df = sorted_df.sort_values("churn_probability", ascending=False)
    elif sort_by == "Recency (Most Recent)" and "recency_days" in sorted_df.columns:
        sorted_df = sorted_df.sort_values("recency_days", ascending=True)
    elif sort_by == "Orders (Most Frequent)" and "total_orders" in sorted_df.columns:
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

    # Format Display Columns with defensive resolution
    display_df = pd.DataFrame()

    # Customer ID
    if "customer_id" in page_data.columns:
        display_df["Customer ID"] = page_data["customer_id"].astype(str)
    else:
        display_df["Customer ID"] = [f"Cust-{i}" for i in range(start_idx, end_idx)]

    # Segment
    if "rfm_segment" in page_data.columns:
        display_df["Segment"] = page_data["rfm_segment"].fillna("Regular").astype(str)
    else:
        display_df["Segment"] = "Regular"

    # Location
    city_s = page_data["city"].fillna("").astype(str).str.title() if "city" in page_data.columns else ""
    state_s = page_data["state"].fillna("").astype(str).str.upper() if "state" in page_data.columns else ""
    if "city" in page_data.columns and "state" in page_data.columns:
        display_df["Location"] = city_s + ", " + state_s
    elif "city" in page_data.columns:
        display_df["Location"] = city_s
    elif "state" in page_data.columns:
        display_df["Location"] = state_s
    else:
        display_df["Location"] = "Recorded in Ledger"

    # Orders
    if "total_orders" in page_data.columns:
        display_df["Orders"] = page_data["total_orders"].fillna(1).astype(int)
    else:
        display_df["Orders"] = 1

    # Total Spend
    if "total_spend" in page_data.columns:
        display_df["Total Spend"] = page_data["total_spend"].fillna(0.0).map(format_brl)
    else:
        display_df["Total Spend"] = "R$ 0.00"

    # Average Order Value (AOV) - Primary column or dynamic derivation
    if "avg_order_value" in page_data.columns:
        display_df["AOV"] = page_data["avg_order_value"].fillna(0.0).map(format_brl)
    elif "total_spend" in page_data.columns and "total_orders" in page_data.columns:
        orders_safe = page_data["total_orders"].replace(0, np.nan)
        derived_aov = (page_data["total_spend"] / orders_safe).fillna(0.0)
        display_df["AOV"] = derived_aov.map(format_brl)
    elif "total_spend" in page_data.columns:
        display_df["AOV"] = page_data["total_spend"].fillna(0.0).map(format_brl)
    else:
        display_df["AOV"] = "R$ 0.00"

    # Recency
    if "recency_days" in page_data.columns:
        display_df["Recency"] = page_data["recency_days"].fillna(0).astype(int).astype(str) + " days"
    else:
        display_df["Recency"] = "N/A"

    # 12M CLV
    if "predicted_clv" in page_data.columns:
        display_df["12M CLV"] = page_data["predicted_clv"].fillna(0.0).map(format_brl)
    else:
        display_df["12M CLV"] = "R$ 0.00"

    # Churn Risk
    if "churn_probability" in page_data.columns:
        display_df["Churn Risk"] = page_data["churn_probability"].fillna(0.0).map(format_pct)
    else:
        display_df["Churn Risk"] = "0.0%"

    # Value Band
    if "clv_band" in page_data.columns:
        display_df["Value Band"] = page_data["clv_band"].fillna("Standard").astype(str)
    else:
        display_df["Value Band"] = "Standard"

    # Optional Priority Score if present (e.g. from Retention Queue)
    if "priority_score" in page_data.columns:
        display_df["Priority Score"] = page_data["priority_score"].fillna(0.0).map(lambda v: f"{float(v):.1f}")

    st.dataframe(display_df, hide_index=True, use_container_width=True)

    # 1-Click Customer Selection into Customer 360
    if "customer_id" in page_data.columns and len(page_data["customer_id"].dropna()) > 0:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        sel_col1, sel_col2 = st.columns([0.65, 0.35])
        with sel_col1:
            cust_choices = page_data["customer_id"].dropna().astype(str).tolist()
            if cust_choices:
                def _format_choice(cid: str) -> str:
                    sub = page_data[page_data["customer_id"].astype(str) == str(cid)]
                    if not sub.empty:
                        seg = sub["rfm_segment"].iloc[0] if "rfm_segment" in sub.columns else "Customer"
                        spend = format_brl(sub["total_spend"].iloc[0]) if "total_spend" in sub.columns else "R$ 0"
                        return f"Customer #{cid} — {seg} ({spend})"
                    return f"Customer #{cid}"

                picked_cust = st.selectbox(
                    "Select a customer from this page to inspect in Customer 360:",
                    cust_choices,
                    format_func=_format_choice,
                    key=f"{key_prefix}_select_cid",
                )
        with sel_col2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 View Customer 360 Profile", key=f"{key_prefix}_open_btn", type="primary", use_container_width=True):
                st.session_state.selected_customer_id = picked_cust
                st.session_state.active_page = "Customer 360"
                st.rerun()
