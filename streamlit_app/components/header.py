"""Global header and workspace header components for CustomerAtlas.

Provides enterprise application branding, honest platform metadata,
category hierarchy badges, and workspace capability breadcrumbs.
"""

from datetime import datetime
from typing import List, Optional
import streamlit as st


def render_global_header(total_profiles: int = 94983) -> None:
    """Render the top enterprise application status bar with honest status."""
    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    st.markdown(
        f"""
        <div class="global-header-bar">
            <div class="global-header-brand">
                <div class="global-header-logo">CA</div>
                <div>
                    <div class="global-header-title">CustomerAtlas</div>
                    <div class="global-header-sub">Unified Customer Intelligence Platform</div>
                </div>
            </div>
            <div class="global-header-meta">
                <div class="meta-pill">
                    <span class="status-badge-neutral">
                        <span class="status-dot-neutral"></span>
                        Analytics Platform
                    </span>
                </div>
                <div class="meta-pill">
                    <span>👥 Canonical Profiles: <strong>{total_profiles:,}</strong></span>
                </div>
                <div class="meta-pill">
                    <span>🇧🇷 Scope: <strong>BRL (R$)</strong></span>
                </div>
                <div class="meta-pill">
                    <span>🕒 Data Sync: <strong>{now_str}</strong></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    page_name: str,
    title: str,
    subtitle: str,
    category_badge: str = "CUSTOMER INTELLIGENCE",
    guides: Optional[List[str]] = None,
) -> None:
    """Render the standard page header with title, subtitle, and capability pills."""
    guide_html = ""
    if guides:
        pills = "".join(f'<span class="guide-pill">✓ {g}</span>' for g in guides)
        guide_html = f"""
        <div class="guide-bar">
            <strong>Key Capabilities:</strong>
            {pills}
        </div>
        """

    st.markdown(
        f"""
        <div class="page-header-container">
            <div>
                <div class="page-badge">{category_badge}</div>
                <h1 class="page-title">{title}</h1>
                <p class="page-subtitle">{subtitle}</p>
            </div>
        </div>
        {guide_html}
        """,
        unsafe_allow_html=True,
    )
