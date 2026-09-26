"""Customer Profile Presentation Components for CustomerAtlas.

Provides enterprise UI components for:
- Customer 360 Header & Hero Dossier
- Customer Multi-Dimensional Health Matrix
- Customer Lifecycle Journey Milestones
- Customer Activity Timeline (Real purchases & reviews)
- Customer Risk Diagnostic Indicators
- RFM Factor Breakdown
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
from utils.formatting import format_brl, format_pct


def render_customer_360_header(
    customer_id: str,
    rfm_segment: str,
    city: str,
    state: str,
    first_purchase_date: Any,
    risk_level: str,
    risk_color: str,
    action_tier: str,
    action_color: str,
) -> None:
    """Render the top enterprise header for the Customer 360 profile."""
    if hasattr(first_purchase_date, "strftime"):
        date_display = first_purchase_date.strftime("%B %d, %Y")
    elif first_purchase_date and str(first_purchase_date).strip() != "":
        try:
            date_display = pd.to_datetime(first_purchase_date).strftime("%B %d, %Y")
        except Exception:
            date_display = str(first_purchase_date)[:10]
    else:
        date_display = "Recorded in Ledger"

    initial = rfm_segment[0] if rfm_segment else "C"
    html = (
        f'<div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">'
        f'<div style="display: flex; align-items: center; gap: 16px;">'
        f'<div style="width: 52px; height: 52px; border-radius: 12px; background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; font-weight: 800; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25);">{initial}</div>'
        f'<div>'
        f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'
        f'<span style="font-size: 19px; font-weight: 800; color: #0F172A; font-family: monospace;">Customer #{customer_id}</span>'
        f'<span style="background: rgba(79, 70, 229, 0.1); color: #4F46E5; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(79, 70, 229, 0.2);">{rfm_segment}</span>'
        f'<span style="background: {risk_color}18; color: {risk_color}; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 6px; border: 1px solid {risk_color}40;">Risk: {risk_level}</span>'
        f'</div>'
        f'<div style="margin-top: 6px; font-size: 13px; color: #64748B;">📍 Location: <strong style="color: #1E293B;">{city.title()}, {state.upper()}</strong> &nbsp;&bull;&nbsp; 🗓️ Customer Since: <strong style="color: #1E293B;">{date_display}</strong></div>'
        f'</div>'
        f'</div>'
        f'<div style="text-align: right;">'
        f'<div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Retention Playbook</div>'
        f'<span style="background: {action_color}; color: white; padding: 6px 14px; border-radius: 20px; font-size: 12.5px; font-weight: 700; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{action_tier}</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_customer_health_grid(health_indicators: List[Dict[str, Any]]) -> None:
    """Render 6-dimension visual customer health cards."""
    st.markdown('<div class="section-header"><h3>Customer Health & Operational Vital Signs</h3><span>Normalized Behavioral Signals</span></div>', unsafe_allow_html=True)
    cols = st.columns(len(health_indicators))
    for idx, item in enumerate(health_indicators):
        with cols[idx]:
            card_html = (
                f'<div style="background: white; border: 1px solid #E2E8F0; border-top: 3px solid {item["color"]}; border-radius: 8px; padding: 14px 12px; text-align: center; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">'
                f'<div style="font-size: 20px; margin-bottom: 4px;">{item["icon"]}</div>'
                f'<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">{item["dimension"]}</div>'
                f'<div style="font-size: 14.5px; font-weight: 800; color: {item["color"]}; margin: 6px 0 4px;">{item["rating"]}</div>'
                f'<div style="font-size: 11px; color: #94A3B8; line-height: 1.3;">{item["detail"]}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)


def render_lifecycle_journey(stages: List[Dict[str, Any]]) -> None:
    """Render customer lifecycle progression milestones."""
    st.markdown('<div class="section-header"><h3>Customer Lifecycle Milestone Progression</h3><span>Verifiable Historical Journey</span></div>', unsafe_allow_html=True)
    cols = st.columns(len(stages))
    for idx, s in enumerate(stages):
        is_reached = s.get("reached", False)
        dot_color = "#4F46E5" if is_reached else "#CBD5E1"
        badge_bg = "rgba(79, 70, 229, 0.08)" if is_reached else "#F8FAFC"
        badge_text = "#4F46E5" if is_reached else "#94A3B8"
        status_icon = "✓" if is_reached else "○"

        with cols[idx]:
            card_html = (
                f'<div style="background: {badge_bg}; border: 1px solid {dot_color}40; border-radius: 8px; padding: 14px; position: relative; height: 100%;">'
                f'<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">'
                f'<span style="font-weight: 800; color: {dot_color}; font-size: 14px;">{status_icon}</span>'
                f'<span style="font-size: 12px; font-weight: 700; color: {badge_text}; text-transform: uppercase;">{s["stage"]}</span>'
                f'</div>'
                f'<div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 2px;">{s["date"]}</div>'
                f'<div style="font-size: 11px; color: #64748B;">{s["description"]}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)


def render_customer_timeline(
    cust_orders: pd.DataFrame,
    cust_reviews: Optional[pd.DataFrame] = None,
) -> None:
    """Render a chronological activity timeline of verified purchases and reviews."""
    events = []

    # Process order events
    if cust_orders is not None and not cust_orders.empty:
        for _, order in cust_orders.iterrows():
            p_date = order.get("purchase_date")
            date_str = str(p_date)[:10] if pd.notna(p_date) else "Recorded Date"
            rev = float(order.get("revenue", order.get("item_price", 0.0)))
            order_id = str(order.get("order_id", ""))[:8]
            status_val = str(order.get("order_status", "delivered")).capitalize()

            events.append({
                "date": p_date,
                "date_display": date_str,
                "type": "purchase",
                "title": f"Completed Purchase (#{order_id})",
                "description": f"Status: {status_val} • Value: {format_brl(rev)}",
                "icon": "🛍️",
                "badge_color": "#4F46E5",
            })

    # Process review events
    if cust_reviews is not None and not cust_reviews.empty:
        for _, rev_row in cust_reviews.iterrows():
            r_date = rev_row.get("review_creation_date", rev_row.get("review_answer_timestamp"))
            date_str = str(r_date)[:10] if pd.notna(r_date) else "Recorded Date"
            score = int(rev_row.get("review_score", 5))
            comment = str(rev_row.get("review_comment_message", ""))
            stars = "⭐" * score

            events.append({
                "date": r_date,
                "date_display": date_str,
                "type": "review",
                "title": f"Submitted Review ({score}/5.0 Stars {stars})",
                "description": f'"{comment[:80]}..."' if comment and comment != "nan" else "Rating submitted without comment text.",
                "icon": "⭐",
                "badge_color": "#16A34A" if score >= 4 else "#DC2626" if score <= 2 else "#F59E0B",
            })

    if not events:
        st.info("No chronological transaction or review timestamps available for this profile.")
        return

    # Sort events chronologically descending
    events.sort(key=lambda x: str(x["date"]) if pd.notna(x["date"]) else "", reverse=True)

    st.markdown('<div class="section-header"><h3>Customer Activity Timeline</h3><span>Chronological Interaction History</span></div>', unsafe_allow_html=True)
    
    timeline_html = ['<div style="position: relative; padding-left: 24px; border-left: 2px solid #E2E8F0; margin-left: 12px;">']
    for ev in events:
        timeline_html.append(
            f"""
            <div style="position: relative; margin-bottom: 20px;">
                <div style="position: absolute; left: -31px; top: 0; width: 16px; height: 16px; border-radius: 50%; background: {ev['badge_color']}; border: 3px solid white; box-shadow: 0 0 0 1px #E2E8F0;"></div>
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 13.5px; font-weight: 700; color: #0F172A;">{ev['icon']} {ev['title']}</span>
                        <span style="font-size: 11.5px; font-weight: 600; color: #64748B; background: #F1F5F9; padding: 2px 8px; border-radius: 4px;">🗓️ {ev['date_display']}</span>
                    </div>
                    <div style="font-size: 12.5px; color: #475569;">{ev['description']}</div>
                </div>
            </div>
            """
        )
    timeline_html.append('</div>')
    st.markdown("".join(timeline_html), unsafe_allow_html=True)


def render_risk_diagnostics(diag: Dict[str, Any], action_info: Dict[str, str]) -> None:
    """Render customer-level risk indicators and retention action."""
    st.markdown('<div class="section-header"><h3>Customer Retention & Risk Diagnostics</h3><span>Empirical Evidence Factors</span></div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([0.55, 0.45])
    with col_l:
        st.markdown("**Identified Risk Signals (Inactivity / Friction):**")
        if diag["risk_factors"]:
            for f in diag["risk_factors"]:
                st.markdown(
                    f'<div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px; font-size: 13px; color: #334155;"><span style="color: #DC2626; font-weight: 800;">⚠️</span><span>{f}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span style="color: #16A34A; font-size: 13px;">✓ No major negative churn indicators detected.</span>', unsafe_allow_html=True)

        if diag["protective_factors"]:
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("**Protective Customer Assets:**")
            for p in diag["protective_factors"]:
                st.markdown(
                    f'<div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px; font-size: 13px; color: #334155;"><span style="color: #16A34A; font-weight: 800;">🛡️</span><span>{p}</span></div>',
                    unsafe_allow_html=True,
                )

    with col_r:
        card_html = (
            f'<div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; border-left: 4px solid {action_info["badge_color"]};">'
            f'<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 4px;">Recommended Next Action</div>'
            f'<div style="font-size: 15px; font-weight: 800; color: #0F172A; margin-bottom: 8px;">{action_info["tier"]} — Urgency: {action_info.get("urgency", "Standard")}</div>'
            f'<p style="font-size: 13px; color: #475569; line-height: 1.45; margin-bottom: 8px;">{action_info["action"]}</p>'
            f'<div style="font-size: 11.5px; font-weight: 600; color: #0284C7; background: #F0F9FF; padding: 6px 10px; border-radius: 4px;">💰 {diag["exposure_note"]}</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
