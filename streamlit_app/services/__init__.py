"""Services package for CustomerAtlas enterprise application layer."""

from services.data_service import (
    load_csv,
    load_model,
    model_input_frame,
    retention_action,
    build_customer_pdf,
    MODEL_COLUMNS,
)
from services.customer_service import (
    get_customer_profile,
    search_customers,
    compute_customer_health,
    derive_lifecycle_stages,
    diagnose_customer_risk_factors,
    explain_rfm_segment,
)
from services.rfm_service import (
    compute_rfm_overview,
    compute_segment_distribution,
    compare_segments,
    get_segment_playbook,
)
from services.clv_service import (
    compute_clv_overview,
    compute_clv_bins,
    analyze_high_value_cohort,
)
from services.risk_service import (
    compute_risk_overview,
    compute_risk_distribution,
    calculate_customer_prioritization,
    compute_quadrant_matrix,
)
from services.model_service import (
    load_ml_model,
    get_model_metadata,
    create_model_input_frame,
    predict_churn_propensity,
    predict_forward_clv,
    audit_model_registry,
    TABULAR_MODEL_FEATURES,
)
from services.data_quality_service import run_data_quality_audit
from services.insight_service import generate_executive_insights
from services.recommendation_service import (
    get_customer_recommendations,
    summarize_recommendation_methods,
)
from services.health_score_service import (
    calculate_customer_health_score,
    classify_lifecycle_state,
)
from services.drift_service import (
    calculate_psi,
    run_feature_drift_audit,
)
from services.simulation_service import (
    simulate_customer_value_shift,
)
from services.explainability_service import (
    get_global_feature_importance,
    explain_individual_prediction,
)
from services.audit_service import (
    record_audit_event,
    get_recent_audit_events,
)
from services.grounded_ai_service import (
    GroundedAIService,
    GroundedAnswer,
)

__all__ = [
    "load_csv",
    "load_model",
    "model_input_frame",
    "retention_action",
    "build_customer_pdf",
    "MODEL_COLUMNS",
    "get_customer_profile",
    "search_customers",
    "compute_customer_health",
    "derive_lifecycle_stages",
    "diagnose_customer_risk_factors",
    "explain_rfm_segment",
    "compute_rfm_overview",
    "compute_segment_distribution",
    "compare_segments",
    "get_segment_playbook",
    "compute_clv_overview",
    "compute_clv_bins",
    "analyze_high_value_cohort",
    "compute_risk_overview",
    "compute_risk_distribution",
    "calculate_customer_prioritization",
    "compute_quadrant_matrix",
    "load_ml_model",
    "get_model_metadata",
    "create_model_input_frame",
    "predict_churn_propensity",
    "predict_forward_clv",
    "audit_model_registry",
    "TABULAR_MODEL_FEATURES",
    "run_data_quality_audit",
    "generate_executive_insights",
    "get_customer_recommendations",
    "summarize_recommendation_methods",
    "calculate_customer_health_score",
    "classify_lifecycle_state",
    "calculate_psi",
    "run_feature_drift_audit",
    "simulate_customer_value_shift",
    "get_global_feature_importance",
    "explain_individual_prediction",
    "record_audit_event",
    "get_recent_audit_events",
    "GroundedAIService",
    "GroundedAnswer",
]
