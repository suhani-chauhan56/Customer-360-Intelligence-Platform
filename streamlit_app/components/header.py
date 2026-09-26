"""Global header and workspace header components for CustomerAtlas.

Provides enterprise application branding, honest platform metadata,
category hierarchy badges, and workspace capability breadcrumbs.
"""

from datetime import datetime
from typing import List, Optional
import streamlit as st


def render_global_header(total_profiles: int = 94983, is_connected: bool = True) -> None:
    """Render the top enterprise application status bar with verified status."""
    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    status_badge = """
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: rgba(22, 163, 74, 0.1); border: 1px solid rgba(22, 163, 74, 0.25); border-radius: 9999px; font-size: 12px; font-weight: 600; color: #16A34A;">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: #16A34A;"></span>
            Data Connected & Analytics Ready
        </span>
    """ if is_connected and total_profiles > 0 else """
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 9999px; font-size: 12px; font-weight: 600; color: #D97706;">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: #D97706;"></span>
            Initializing Data Engine
        </span>
    """

    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 20px; margin-bottom: 22px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 38px; height: 38px; border-radius: 9px; background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 16px; box-shadow: 0 2px 6px rgba(79, 70, 229, 0.3);">CA</div>
                <div>
                    <div style="font-size: 17px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; display: flex; align-items: center; gap: 8px;">
                        CustomerAtlas AI
                    </div>
                    <div style="font-size: 12px; color: #64748B; font-weight: 500;">Unified Customer Intelligence Platform</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                {status_badge}
                <div style="padding: 4px 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 9999px; font-size: 12px; color: #475569; font-weight: 600;">
                    👥 <strong>{total_profiles:,}</strong> Verified Profiles
                </div>
                <div style="padding: 4px 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 9999px; font-size: 12px; color: #475569; font-weight: 600;">
                    🇧🇷 Scope: <strong>BRL (R$)</strong>
                </div>
                <div style="padding: 4px 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 9999px; font-size: 12px; color: #64748B; font-weight: 500;">
                    🕒 {now_str}
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
        pills = "".join(f'<span style="display: inline-flex; align-items: center; padding: 3px 9px; background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 6px; font-size: 11px; font-weight: 600; color: #4338CA; margin-right: 6px; margin-bottom: 4px;">✓ {g}</span>' for g in guides)
        guide_html = f"""
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid #F1F5F9;">
            <span style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Capabilities:</span>
            {pills}
        </div>
        """

    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
            <div>
                <span style="display: inline-block; padding: 3px 8px; background: #EEF2FF; border-radius: 5px; font-size: 10.5px; font-weight: 700; color: #4F46E5; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 6px;">{category_badge}</span>
                <h1 style="font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px 0; letter-spacing: -0.02em;">{title}</h1>
                <p style="font-size: 13.5px; color: #475569; margin: 0; line-height: 1.5;">{subtitle}</p>
            </div>
            {guide_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
