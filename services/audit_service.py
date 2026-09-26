"""Root package proxy for audit_service."""
from streamlit_app.services.audit_service import (
    get_recent_audit_events,
    record_audit_event,
)

__all__ = ["get_recent_audit_events", "record_audit_event"]
