"""Unit tests for enterprise audit logging service."""

import pytest
from services.audit_service import record_audit_event, get_recent_audit_events


def test_record_and_get_audit_event():
    event = record_audit_event(
        action="TEST_ACTION",
        resource_type="Customer",
        resource_id="cust_test_123",
        details="Unit test audit event execution",
    )
    assert event["action"] == "TEST_ACTION"
    assert event["resource_id"] == "cust_test_123"

    recent = get_recent_audit_events(limit=5)
    assert len(recent) > 0
    actions = [r["action"] for r in recent]
    assert "TEST_ACTION" in actions
