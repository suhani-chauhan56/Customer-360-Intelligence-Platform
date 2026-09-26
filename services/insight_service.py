"""Root package proxy for insight_service."""
from streamlit_app.services.insight_service import (
    generate_executive_insights,
)

__all__ = ["generate_executive_insights"]
