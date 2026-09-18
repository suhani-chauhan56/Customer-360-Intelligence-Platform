"""Reusable enterprise KPI card components for CustomerAtlas.

Provides standardized B2B metric presentation supporting labels, values,
delta percentages, trends, and contextual micro-descriptions.
"""

from typing import Any, Dict, List, Optional
import streamlit as st


def render_kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_direction: str = "neutral",  # 'positive', 'negative', or 'neutral'
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
) -> str:
    """Generate HTML markup for a single enterprise KPI card."""
    icon_html = f'<span class="kpi-card-icon">{icon}</span>' if icon else ""

    delta_html = ""
    if delta:
        delta_class = f"kpi-delta-badge {delta_direction}"
        delta_arrow = "▲ " if delta_direction == "positive" else "▼ " if delta_direction == "negative" else ""
        delta_html = f'<span class="{delta_class}">{delta_arrow}{delta}</span>'

    footer_content = ""
    if delta_html or subtitle:
        sub_text = f"<span>{subtitle}</span>" if subtitle else ""
        footer_content = f"""
        <div class="kpi-card-footer">
            {delta_html}
            {sub_text}
        </div>
        """

    return f"""
    <div class="kpi-card">
        <div class="kpi-card-header">
            <span class="kpi-card-label">{label}</span>
            {icon_html}
        </div>
        <div class="kpi-card-value">{value}</div>
        {footer_content}
    </div>
    """


def render_kpi_row(cards: List[Dict[str, Any]]) -> None:
    """Render a row of enterprise KPI cards dynamically sized across columns.

    Each card dict accepts:
        - label (str)
        - value (str)
        - delta (Optional[str])
        - delta_direction (Optional[str]: 'positive', 'negative', 'neutral')
        - subtitle (Optional[str])
        - icon (Optional[str])
    """
    if not cards:
        return

    cols = st.columns(len(cards))
    for idx, card_def in enumerate(cards):
        with cols[idx]:
            html = render_kpi_card(
                label=card_def.get("label", ""),
                value=card_def.get("value", "0"),
                delta=card_def.get("delta"),
                delta_direction=card_def.get("delta_direction", "neutral"),
                subtitle=card_def.get("subtitle"),
                icon=card_def.get("icon"),
            )
            st.markdown(html, unsafe_allow_html=True)
