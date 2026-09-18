"""Customer Profile Presentation Components for CustomerAtlas.

Provides enterprise UI components for:
- Customer 360 Header & Hero Dossier
- Customer Multi-Dimensional Health Matrix
- Customer Lifecycle Journey Milestones
- Customer Risk Diagnostic Indicators
- RFM Factor Breakdown
"""

from typing import Any, Dict, List
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

    html = f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 56px; height: 56px; border-radius: 12px; background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: 800; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);">
                {rfm_segment[0] if rfm_segment else "C"}
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <span style="font-size: 20px; font-weight: 800; color: #0F172A; font-family: 'JetBrains Mono', monospace;">Customer #{customer_id}</span>
                    <span style="background: rgba(79, 70, 229, 0.1); color: #4F46E5; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(79, 70, 229, 0.2);">
                        {rfm_segment}
                    </span>
                    <span style="background: {risk_color}18; color: {risk_color}; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 6px; border: 1px solid {risk_color}40;">
                        Risk: {risk_level}
                    </span>
                </div>
                <div style="margin-top: 6px; font-size: 13px; color: #64748B;">
                    📍 Location: <strong style="color: #1E293B;">{city.title()}, {state.upper()}</strong> &nbsp;&bull;&nbsp;
                    🗓️ Customer Since: <strong style="color: #1E293B;">{date_display}</strong>
                </div>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Retention Playbook</div>
            <span style="background: {action_color}; color: white; padding: 6px 14px; border-radius: 20px; font-size: 12.5px; font-weight: 700; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                {action_tier}
            </span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_customer_health_grid(health_indicators: List[Dict[str, Any]]) -> None:
    """Render 6-dimension visual customer health cards."""
    st.markdown(
        """
        <div class="section-header">
            <h3>Customer Health & Operational Vital Signs</h3>
            <span>Normalized Behavioral Signals</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(health_indicators))
    for idx, item in enumerate(health_indicators):
        with cols[idx]:
            card_html = f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-top: 3px solid {item['color']}; border-radius: 8px; padding: 14px 12px; text-align: center; height: 100%;">
                <div style="font-size: 20px; margin-bottom: 4px;">{item['icon']}</div>
                <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">{item['dimension']}</div>
                <div style="font-size: 14.5px; font-weight: 800; color: {item['color']}; margin: 6px 0 4px;">{item['rating']}</div>
                <div style="font-size: 11px; color: #94A3B8; line-height: 1.3;">{item['detail']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)


def render_lifecycle_journey(stages: List[Dict[str, Any]]) -> None:
    """Render customer lifecycle progression milestones."""
    st.markdown(
        """
        <div class="section-header">
            <h3>Customer Lifecycle Milestone Progression</h3>
            <span>Verifiable Historical Journey</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(stages))
    for idx, s in enumerate(stages):
        is_reached = s.get("reached", False)
        dot_color = "#4F46E5" if is_reached else "#CBD5E1"
        badge_bg = "rgba(79, 70, 229, 0.1)" if is_reached else "#F1F5F9"
        badge_text = "#4F46E5" if is_reached else "#94A3B8"
        status_icon = "✓" if is_reached else "○"

        with cols[idx]:
            st.markdown(
                f"""
                <div style="background: {badge_bg}; border: 1px solid {dot_color}40; border-radius: 8px; padding: 14px; position: relative; height: 100%;">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                        <span style="font-weight: 800; color: {dot_color}; font-size: 14px;">{status_icon}</span>
                        <span style="font-size: 12px; font-weight: 700; color: {badge_text}; text-transform: uppercase;">{s['stage']}</span>
                    </div>
                    <div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 2px;">{s['date']}</div>
                    <div style="font-size: 11px; color: #64748B;">{s['description']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_risk_diagnostics(diag: Dict[str, Any], action_info: Dict[str, str]) -> None:
    """Render customer-level risk indicators and retention action."""
    st.markdown(
        """
        <div class="section-header">
            <h3>Customer Retention & Risk Diagnostics</h3>
            <span>Empirical Evidence Factors</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([0.55, 0.45])
    with col_l:
        st.markdown("**Identified Risk Signals (Inactivity / Friction):**")
        if diag["risk_factors"]:
            for f in diag["risk_factors"]:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px; font-size: 13px; color: #334155;">
                        <span style="color: #DC2626; font-weight: 800;">⚠️</span>
                        <span>{f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span style="color: #16A34A; font-size: 13px;">✓ No major negative churn indicators detected.</span>', unsafe_allow_html=True)

        if diag["protective_factors"]:
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("**Protective Customer Assets:**")
            for p in diag["protective_factors"]:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px; font-size: 13px; color: #334155;">
                        <span style="color: #16A34A; font-weight: 800;">🛡️</span>
                        <span>{p}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col_r:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; border-left: 4px solid {action_info['badge_color']};">
                <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 4px;">Recommended Next Action</div>
                <div style="font-size: 15px; font-weight: 800; color: #0F172A; margin-bottom: 8px;">{action_info['tier']} — Urgency: {action_info.get('urgency', 'Standard')}</div>
                <p style="font-size: 13px; color: #475569; line-height: 1.45; margin-bottom: 8px;">{action_info['action']}</p>
                <div style="font-size: 11.5px; font-weight: 600; color: #0284C7; background: #F0F9FF; padding: 6px 10px; border-radius: 4px;">
                    💰 {diag['exposure_note']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
