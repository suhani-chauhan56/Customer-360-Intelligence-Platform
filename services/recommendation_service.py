"""Root package proxy for recommendation_service."""
from streamlit_app.services.recommendation_service import (
    RECOMMENDATION_RULES,
    compute_recommendation_portfolio,
    compute_recommendation_summary,
    generate_customer_recommendation,
    get_customer_recommendations,
)

__all__ = [
    "RECOMMENDATION_RULES",
    "compute_recommendation_portfolio",
    "compute_recommendation_summary",
    "generate_customer_recommendation",
    "get_customer_recommendations",
]
