"""Enterprise design system and visualization styling utilities for CustomerAtlas.

Ensures consistent visual language, Plotly chart theming, and centralized
CSS injection following the B2B SaaS design system.
"""

from pathlib import Path
from typing import Optional
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# DESIGN SYSTEM PALETTE
# ==============================================================================

COLOR_PRIMARY = "#4F46E5"        # Indigo
COLOR_PRIMARY_HOVER = "#4338CA"
COLOR_CYAN = "#06B6D4"
COLOR_PURPLE = "#8B5CF6"
COLOR_AMBER = "#F59E0B"           # Warning
COLOR_RED = "#DC2626"             # Danger
COLOR_GREEN = "#16A34A"           # Success
COLOR_SLATE = "#0F172A"           # Primary Text
COLOR_SECONDARY = "#64748B"       # Secondary Text
COLOR_MUTED = "#94A3B8"           # Muted Text
COLOR_BORDER = "#E2E8F0"
COLOR_SURFACE = "#FFFFFF"
COLOR_PAGE_BG = "#F8FAFC"

CHART_COLORWAY = [
    "#4F46E5",  # Primary Indigo
    "#06B6D4",  # Cyan
    "#8B5CF6",  # Purple
    "#F59E0B",  # Amber
    "#16A34A",  # Green
    "#EC4899",  # Pink
    "#3B82F6",  # Blue
]

PLOT_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


def load_css() -> None:
    """Read centralized assets/style.css and inject it into the Streamlit session."""
    # Search for assets/style.css across standard locations
    candidate_paths = [
        Path(__file__).resolve().parent.parent / "streamlit_app" / "assets" / "style.css",
        Path(__file__).resolve().parent / "assets" / "style.css",
        Path.cwd() / "streamlit_app" / "assets" / "style.css",
        Path.cwd() / "assets" / "style.css",
    ]
    css_content = None
    for cp in candidate_paths:
        if cp.exists():
            with open(cp, "r", encoding="utf-8") as f:
                css_content = f.read()
            break

    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS asset not found.")


def style_chart(
    figure: go.Figure,
    height: int = 320,
    legend: str = "bottom",
    title: Optional[str] = None,
    dark_mode: bool = False,
) -> None:
    """Apply consistent enterprise B2B styling to any Plotly chart.

    Parameters:
        figure: The Plotly figure object
        height: Height in pixels
        legend: 'bottom', 'top', 'right', or 'hidden'
        title: Optional override title
        dark_mode: Maintained for interface compatibility
    """
    text_color = COLOR_SECONDARY
    title_color = COLOR_SLATE
    grid_color = "rgba(226, 232, 240, 0.8)"  # Slate 200
    hover_bg = COLOR_SURFACE
    hover_text = COLOR_SLATE

    show_legend = legend != "hidden"
    if legend == "top":
        legend_layout = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=text_color, family="Plus Jakarta Sans, Inter"),
        )
    elif legend == "bottom":
        legend_layout = dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=text_color, family="Plus Jakarta Sans, Inter"),
        )
    else:
        legend_layout = dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color=text_color, family="Plus Jakarta Sans, Inter"),
        )

    bottom_margin = 52 if (show_legend and legend == "bottom") else 24

    figure.update_layout(
        height=height,
        margin=dict(l=16, r=16, t=44, b=bottom_margin),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CHART_COLORWAY,
        font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color=text_color, size=12),
        title=dict(
            text=title or (figure.layout.title.text if hasattr(figure.layout, "title") and figure.layout.title else None),
            font=dict(size=14.5, color=title_color, family="Plus Jakarta Sans", weight=700),
            x=0.01,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ),
        showlegend=show_legend,
        legend=legend_layout,
        hoverlabel=dict(
            bgcolor=hover_bg,
            font_color=hover_text,
            bordercolor=COLOR_BORDER,
            font_size=12,
            font_family="Plus Jakarta Sans, Inter, sans-serif",
        ),
    )

    figure.update_xaxes(
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        linecolor=COLOR_BORDER,
        tickfont=dict(color=text_color, size=11),
    )
    figure.update_yaxes(
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        linecolor=COLOR_BORDER,
        tickfont=dict(color=text_color, size=11),
    )

    st.plotly_chart(figure, use_container_width=True, config=PLOT_CONFIG)


# Compatibility alias
def chart(figure: go.Figure, height: int = 320, legend: str = "bottom", dark_mode: bool = False) -> None:
    style_chart(figure=figure, height=height, legend=legend, dark_mode=dark_mode)


__all__ = [
    "COLOR_PRIMARY",
    "COLOR_PRIMARY_HOVER",
    "COLOR_CYAN",
    "COLOR_PURPLE",
    "COLOR_AMBER",
    "COLOR_RED",
    "COLOR_GREEN",
    "COLOR_SLATE",
    "COLOR_SECONDARY",
    "COLOR_MUTED",
    "COLOR_BORDER",
    "COLOR_SURFACE",
    "COLOR_PAGE_BG",
    "CHART_COLORWAY",
    "PLOT_CONFIG",
    "load_css",
    "style_chart",
    "chart",
]
