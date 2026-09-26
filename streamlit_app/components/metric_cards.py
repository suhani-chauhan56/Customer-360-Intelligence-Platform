"""Enterprise KPI metric card components for CustomerAtlas.

Provides native, robust B2B metric presentation supporting labels, values,
deltas, trends, icons, and contextual micro-descriptions with zero raw HTML leakage.
"""

from typing import Any, Dict, List, Optional
import streamlit as st


def render_kpi_row(cards: List[Dict[str, Any]]) -> None:
    """Render a row of enterprise KPI cards using native Streamlit containers and metrics.

    Each card dict accepts:
        - label (str): Metric label/title
        - value (str): Primary formatted value
        - delta (Optional[str]): Delta change value
        - delta_direction (Optional[str]): 'positive', 'negative', 'neutral'
        - subtitle (Optional[str]): Micro-description or context
        - icon (Optional[str]): Emoji or icon prefix
    """
    if not cards:
        return

    cols = st.columns(len(cards))
    for idx, card_def in enumerate(cards):
        with cols[idx]:
            with st.container(border=True):
                label = card_def.get("label", "")
                icon = card_def.get("icon", "")
                icon_prefix = f"{icon} " if icon else ""
                
                delta = card_def.get("delta")
                direction = card_def.get("delta_direction", "neutral")
                
                if direction == "positive":
                    delta_color = "normal"
                elif direction == "negative":
                    delta_color = "inverse"
                else:
                    delta_color = "off"

                st.metric(
                    label=f"{icon_prefix}{label}",
                    value=card_def.get("value", "0"),
                    delta=delta,
                    delta_color=delta_color if delta else "off",
                )
                
                subtitle = card_def.get("subtitle")
                if subtitle:
                    st.caption(subtitle)


def render_kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_direction: str = "neutral",
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
) -> None:
    """Render a single enterprise KPI card in the active column."""
    with st.container(border=True):
        icon_prefix = f"{icon} " if icon else ""
        direction = delta_direction.lower()
        if direction == "positive":
            delta_color = "normal"
        elif direction == "negative":
            delta_color = "inverse"
        else:
            delta_color = "off"

        st.metric(
            label=f"{icon_prefix}{label}",
            value=value,
            delta=delta,
            delta_color=delta_color if delta else "off",
        )
        if subtitle:
            st.caption(subtitle)
