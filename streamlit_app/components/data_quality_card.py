"""System Health, Data Quality, Drift Monitoring, and Enterprise Governance Console.

Renders factual data contract checks, model artifact registry status, PSI feature
drift monitoring, enterprise audit logs, and REST API readiness.
"""

from typing import Any, Dict
import pandas as pd
import streamlit as st

from config.settings import get_environment_info
from services.audit_service import get_recent_audit_events
from services.data_quality_service import run_data_quality_audit
from services.drift_service import run_feature_drift_audit
from services.model_service import audit_model_registry
from utils.helpers import calculate_data_snapshot_info


def render_system_health_modal(customer_features: pd.DataFrame) -> None:
    """Render the comprehensive Enterprise System Health & Governance console."""
    with st.expander("🛠️ Enterprise System Health & Governance Console", expanded=False, icon=":material/admin_panel_settings:"):
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
            st.metric("Architecture", "Modular Monolith", delta=f"Release {env_info['app_version']}")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        tab_data, tab_models, tab_drift, tab_audit, tab_api = st.tabs([
            "📊 Data Contract Audits",
            "🤖 ML Model Registry",
            "📈 MLOps Feature Drift",
            "🛡️ Enterprise Audit Logs",
            "🌐 REST API & Database",
        ])

        with tab_data:
            st.markdown("**Automated Feature Store Integrity Checks:**")
            st.dataframe(pd.DataFrame(audit_res["checks"]), hide_index=True, use_container_width=True)

        with tab_models:
            st.markdown("**Validated Machine Learning Artifacts:**")
            st.dataframe(pd.DataFrame(model_reg), hide_index=True, use_container_width=True)

        with tab_drift:
            st.markdown("**Population Stability Index (PSI) Feature Drift Analysis:**")
            if not customer_features.empty and "recency_days" in customer_features.columns:
                baseline_sub = customer_features[customer_features["recency_days"] > 180]
                current_sub = customer_features[customer_features["recency_days"] <= 180]
                drift_res = run_feature_drift_audit(baseline_sub, current_sub)
                
                st.caption(f"Status: **{drift_res['overall_status']}** | Policy: {drift_res['governance_policy']}")
                st.dataframe(pd.DataFrame(drift_res["features"]), hide_index=True, use_container_width=True)
            else:
                st.info("Insufficient longitudinal data for drift monitoring.")

        with tab_audit:
            st.markdown("**Real-Time Enterprise Compliance Event Stream:**")
            recent_logs = get_recent_audit_events(limit=15)
            if recent_logs:
                st.dataframe(pd.DataFrame(recent_logs), hide_index=True, use_container_width=True)
            else:
                st.info("No compliance audit events recorded in active session.")

        with tab_api:
            st.markdown("**FastAPI Micro-Framework & Relational Repository Engine:**")
            st.info(
                "• REST API endpoints exposed under `/api/v1/customers`, `/api/v1/segments`, `/api/v1/analytics`, `/api/v1/ml`, `/api/v1/system`.\n"
                "• Interactive Swagger OpenAPI documentation accessible at `http://localhost:8000/api/docs`.\n"
                "• Database readiness with SQLAlchemy Repository Pattern supporting SQLite / PostgreSQL."
            )
            env_rows = [
                {"Parameter": "Application Name", "Configuration Value": env_info["app_name"]},
                {"Parameter": "Software Version", "Configuration Value": env_info["app_version"]},
                {"Parameter": "Runtime Environment", "Configuration Value": env_info["environment"]},
                {"Parameter": "Memory Footprint", "Configuration Value": f"{snapshot_info['memory_mb']} MB"},
                {"Parameter": "OpenAPI Documentation", "Configuration Value": "/api/docs"},
                {"Parameter": "Currency Format", "Configuration Value": env_info["currency"]},
            ]
            st.dataframe(pd.DataFrame(env_rows), hide_index=True, use_container_width=True)
