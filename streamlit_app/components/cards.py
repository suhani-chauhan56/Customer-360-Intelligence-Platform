"""Card, container, empty-state, and error-state components for CustomerAtlas.

Provides uniform cards for business insights, next-best-category offers,
customer dossiers, and resilient fallback states.
"""

from typing import Any, Dict, List, Optional
import streamlit as st


def render_insight_card(
    title: str,
    description: str,
    kind: str = "info",  # 'info', 'warning', 'alert', 'success'
) -> str:
    """Generate HTML for an enterprise insight card with status color accent."""
    class_name = f"insight-card {kind}" if kind in {"warning", "alert", "info", "success"} else "insight-card"
    return f"""
    <div class="{class_name}">
        <div class="insight-title">{title}</div>
        <p class="insight-desc">{description}</p>
    </div>
    """


def render_insight_grid(insights: List[Dict[str, str]]) -> None:
    """Render a responsive grid of insight cards.

    Each insight dict: {"title": str, "description": str, "kind": Optional[str]}
    """
    if not insights:
        return
    cards_html = "".join(
        render_insight_card(
            title=item.get("title", ""),
            description=item.get("description", ""),
            kind=item.get("kind", "info"),
        )
        for item in insights
    )
    st.markdown(f'<div class="insight-grid">{cards_html}</div>', unsafe_allow_html=True)


def render_recommendation_card(
    rank: int,
    category: str,
    reason: str,
    method: str = "Basket Association",
) -> str:
    """Generate HTML for an explainable Next-Best-Offer recommendation card."""
    return f"""
    <div class="rec-card">
        <span class="rec-card-rank">#{rank}</span>
        <div class="rec-card-title">{category}</div>
        <p class="rec-card-reason"><strong>Logic:</strong> {reason}</p>
        <div style="margin-top: 8px; font-size: 11px; color: var(--primary); font-weight: 600;">
            Engine: {method}
        </div>
    </div>
    """


def render_customer_hero(
    customer_id: str,
    rfm_segment: str,
    cluster_segment: str,
    city: str,
    state: str,
    favorite_category: str,
    clv_band: str,
    action_tier: str,
    action_badge_color: str,
) -> None:
    """Render the top profile summary card in the Customer 360 Dossier."""
    initial = str(rfm_segment)[0] if rfm_segment else "C"
    st.markdown(
        f"""
        <div class="customer-hero-card">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="width: 52px; height: 52px; border-radius: 10px; background: var(--primary); display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; font-weight: 800; box-shadow: 0 2px 8px rgba(79, 70, 229, 0.35);">
                    {initial}
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <span style="font-size: 18px; font-weight: 800; color: var(--text-primary); font-family: 'JetBrains Mono', monospace;">{customer_id}</span>
                        <span style="background: rgba(79, 70, 229, 0.1); color: var(--primary); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">{rfm_segment}</span>
                        <span style="background: rgba(6, 182, 212, 0.1); color: #0284C7; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">{cluster_segment}</span>
                    </div>
                    <p style="margin: 4px 0 0; font-size: 13px; color: var(--text-secondary);">
                        📍 {city.title()}, {state.upper()} &nbsp;|&nbsp;
                        Affinity Category: <strong>{favorite_category}</strong> &nbsp;|&nbsp;
                        Value Tier: <strong>{clv_band}</strong>
                    </p>
                </div>
            </div>
            <div>
                <span style="background: {action_badge_color}; color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    {action_tier}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(
    title: str = "No data available",
    description: str = "No records match the current filter selection.",
    show_reset: bool = True,
) -> None:
    """Render a clean enterprise empty state with optional reset action."""
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <div class="empty-state-title">{title}</div>
            <div class="empty-state-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if show_reset:
        col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
        with col2:
            if st.button("Reset Filters", key="empty_state_reset_btn", icon=":material/restart_alt:", use_container_width=True):
                st.session_state.reset_filters_flag = True
                st.rerun()


def render_error_state(
    title: str = "Something went wrong",
    description: str = "An unexpected issue occurred while processing this analysis. Please refresh the page or adjust filter criteria.",
) -> None:
    """Render a graceful enterprise error card."""
    st.markdown(
        f"""
        <div class="error-state">
            <div class="error-state-title">⚠️ {title}</div>
            <div class="error-state-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
