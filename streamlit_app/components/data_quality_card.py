"""System Health and Data Quality Presentation Component for CustomerAtlas.

Renders factual data contract checks, model artifact registry status, and
dataset snapshot metadata for production transparency.
"""

from typing import Any, Dict
import pandas as pd
import streamlit as st

from config.settings import get_environment_info
from services.data_quality_service import run_data_quality_audit
from services.model_service import audit_model_registry
from utils.helpers import calculate_data_snapshot_info


def render_system_health_modal(customer_features: pd.DataFrame) -> None:
    """Render an expandable or tabbed System Health and Governance console."""
    with st.expander("🛠️ System Health & Data Quality Console", expanded=False):
        audit_res = run_data_quality_audit(customer_features)
        env_info = get_environment_info()
        snapshot_info = calculate_data_snapshot_info(customer_features)
        model_reg = audit_model_registry()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Data Quality Score", f"{audit_res['quality_score_pct']}%", delta="100% Target" if audit_res["is_healthy"] else "-Issues")
        with c2:
            st.metric("Canonical Profiles", f"{snapshot_info['rows']:,}", delta=f"{snapshot_info['columns']} features")
        with c3:
            ready_models = sum(1 for m in model_reg if "Ready" in m["Status"])
            st.metric("ML Models Ready", f"{ready_models}/{len(model_reg)}", delta="All Verified" if ready_models == len(model_reg) else "Missing")
        with c4:
            st.metric("Environment", env_info["environment"].upper(), delta=f"Release {env_info['app_version']}")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        tab_data, tab_models, tab_env = st.tabs(["📊 Data Contract Audits", "🤖 ML Model Registry", "⚙️ Runtime Environment"])

        with tab_data:
            st.markdown("**Automated Feature Store Integrity Checks:**")
            st.dataframe(pd.DataFrame(audit_res["checks"]), hide_index=True, use_container_width=True)

        with tab_models:
            st.markdown("**Validated Machine Learning Artifacts:**")
            st.dataframe(pd.DataFrame(model_reg), hide_index=True, use_container_width=True)

        with tab_env:
            env_rows = [
                {"Parameter": "Application Name", "Configuration Value": env_info["app_name"]},
                {"Parameter": "Software Version", "Configuration Value": env_info["app_version"]},
                {"Parameter": "Runtime Environment", "Configuration Value": env_info["environment"]},
                {"Parameter": "Log Level", "Configuration Value": env_info["log_level"]},
                {"Parameter": "Memory Footprint", "Configuration Value": f"{snapshot_info['memory_mb']} MB"},
                {"Parameter": "Currency Format", "Configuration Value": env_info["currency"]},
            ]
            st.dataframe(pd.DataFrame(env_rows), hide_index=True, use_container_width=True)
