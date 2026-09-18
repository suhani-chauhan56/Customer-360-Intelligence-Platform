"""Grounded AI Assistant UI component for CustomerAtlas.

Renders structured, evidence-backed conversational analytics responses
with complete mathematical transparency and auditability.
"""

from typing import Optional
import streamlit as st
from services.grounded_ai_service import GroundedAnswer
from utils.styling import COLOR_PRIMARY, COLOR_AMBER, COLOR_GREEN, COLOR_RED, COLOR_SLATE


def render_grounded_answer(answer: GroundedAnswer) -> None:
    """Render a structured GroundedAnswer with metrics chips and evidence citations."""
    badge_color = (
        COLOR_PRIMARY if answer.intent not in ["unsupported_or_ambiguous", "empty_query"]
        else COLOR_SLATE
    )
    
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-left: 5px solid {badge_color}; border-radius: 8px; padding: 20px; margin: 16px 0 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; background: #EEF2FF; color: #4F46E5; padding: 3px 8px; border-radius: 4px;">
                    Intent: {answer.intent.replace('_', ' ').title()}
                </span>
                <span style="font-size: 11px; font-weight: 600; color: #059669; background: #ECFDF5; padding: 3px 8px; border-radius: 4px;">
                    ✓ {answer.confidence_rating}
                </span>
            </div>
            <h3 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 800; color: #0F172A; line-height: 1.35;">
                {answer.headline}
            </h3>
            <p style="font-size: 14px; color: #334155; line-height: 1.55; margin-bottom: 16px;">
                {answer.detailed_answer}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # If metrics exist, display metrics chips
    if answer.metrics:
        st.markdown("<div style='font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 6px;'>Verified Metrics Evidence:</div>", unsafe_allow_html=True)
        m_cols = st.columns(min(len(answer.metrics), 4))
        for idx, (m_key, m_val) in enumerate(answer.metrics.items()):
            col_target = m_cols[idx % len(m_cols)]
            with col_target:
                label_fmt = m_key.replace('_', ' ').title()
                val_fmt = f"{m_val:,}" if isinstance(m_val, (int, float)) and m_val > 999 else str(m_val)
                st.metric(label=label_fmt, value=val_fmt)

    # Evidence points
    if answer.evidence_points:
        with st.expander("Grounded Data Citations & Verification Logs", expanded=True, icon=":material/fact_check:"):
            for pt in answer.evidence_points:
                st.markdown(f"• **Data Fact:** {pt}")
            st.caption(f"Source: `{answer.data_source}` | Policy: {answer.limitations_disclaimer}")

    # Recommended action callout
    if answer.recommended_action:
        st.info(f"💡 **Recommended Tactical Next Step:** {answer.recommended_action}")
