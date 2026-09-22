"""Analytics core services module under src."""

from analytics import (
    ExecutiveKPIs,
    calculate_health_score,
    calculate_population_stability_index,
    classify_lifecycle_stage,
    compute_clv_brackets,
    compute_executive_kpis,
    compute_rfm_distribution,
    load_dataset,
    prioritize_retention_queue,
    run_full_analytics_audit,
    validate_dataset,
)

__all__ = [
    "ExecutiveKPIs",
    "compute_executive_kpis",
    "compute_rfm_distribution",
    "compute_clv_brackets",
    "prioritize_retention_queue",
    "calculate_health_score",
    "classify_lifecycle_stage",
    "calculate_population_stability_index",
    "run_full_analytics_audit",
    "load_dataset",
    "validate_dataset",
]
