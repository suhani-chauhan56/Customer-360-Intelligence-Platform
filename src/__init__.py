"""CustomerAtlas Core Source Package."""

from analytics import (
    compute_executive_kpis,
    compute_rfm_distribution,
    compute_clv_brackets,
    prioritize_retention_queue,
    calculate_health_score,
    classify_lifecycle_stage,
    calculate_population_stability_index,
    load_dataset,
    validate_dataset,
)

__all__ = [
    "compute_executive_kpis",
    "compute_rfm_distribution",
    "compute_clv_brackets",
    "prioritize_retention_queue",
    "calculate_health_score",
    "classify_lifecycle_stage",
    "calculate_population_stability_index",
    "load_dataset",
    "validate_dataset",
]
