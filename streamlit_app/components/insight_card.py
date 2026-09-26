"""Structured Business Insight Component for CustomerAtlas.

Implements standard enterprise analytics insight pattern:
- Title / Theme
- Observation (What is happening)
- Evidence (Calculated metric / empirical proof)
- Business Implication (Actionable commercial consequence)
"""

from typing import Dict, List, Optional
import streamlit as st


def render_structured_insight(
    title: str,
    observation: str,
    evidence: str,
    implication: str,
    badge: str = "Analytics Insight",
    kind: str = "info",  # 'info', 'warning', 'alert', 'success'
) -> None:
    """Render an enterprise structured business insight card."""
    accent_color = (
        "#16A34A" if kind == "success"
        else "#DC2626" if kind == "alert"
        else "#F59E0B" if kind == "warning"
        else "#0284C7"
    )

    border_color = (
        "rgba(22, 163, 74, 0.3)" if kind == "success"
        else "rgba(220, 38, 38, 0.3)" if kind == "alert"
        else "rgba(245, 158, 11, 0.3)" if kind == "warning"
        else "rgba(2, 132, 199, 0.3)"
    )

    bg_color = (
        "rgba(22, 163, 74, 0.04)" if kind == "success"
        else "rgba(220, 38, 38, 0.04)" if kind == "alert"
        else "rgba(245, 158, 11, 0.04)" if kind == "warning"
        else "rgba(2, 132, 199, 0.04)"
    )

    html = (
        f'<div style="background: {bg_color}; border: 1px solid {border_color}; border-left: 4px solid {accent_color}; border-radius: 8px; padding: 18px 20px; margin-bottom: 16px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">'
        f'<div style="font-size: 15px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.02em;">{title}</div>'
        f'<span style="font-size: 11px; font-weight: 700; background: {accent_color}; color: white; padding: 3px 9px; border-radius: 12px;">{badge}</span>'
        f'</div>'
        f'<div style="margin-bottom: 8px;"><span style="font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">Observation: </span><span style="font-size: 13.5px; color: #1E293B; line-height: 1.5;">{observation}</span></div>'
        f'<div style="margin-bottom: 8px; background: rgba(255, 255, 255, 0.7); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(0,0,0,0.04);"><span style="font-size: 12px; font-weight: 700; color: #0284C7; text-transform: uppercase; letter-spacing: 0.05em;">📊 Evidence: </span><span style="font-size: 13.5px; font-weight: 600; color: #0F172A;">{evidence}</span></div>'
        f'<div><span style="font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">💡 Commercial Implication: </span><span style="font-size: 13.5px; color: #334155; line-height: 1.5;">{implication}</span></div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
