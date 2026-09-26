"""Root package proxy for grounded_ai_service."""
from streamlit_app.services.grounded_ai_service import (
    GroundedAIService,
    GroundedAnswer,
)

__all__ = ["GroundedAIService", "GroundedAnswer"]
