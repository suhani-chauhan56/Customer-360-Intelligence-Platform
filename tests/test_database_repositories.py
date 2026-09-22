"""Unit tests for Database Repositories and Audit Persistence."""

import pytest
from database.connection import init_db, db_session_scope, SessionFactory
from database.models import Customer, AuditLog
from database.repositories.customer_repository import CustomerRepository
from database.repositories.audit_repository import AuditRepository


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_audit_repository_logging():
    with db_session_scope() as session:
        repo = AuditRepository(session)
        log = repo.log_event(
            action="TEST_ACTION",
            resource_type="TestResource",
            org_id="test_org",
            user_id="test_user",
            resource_id="res_001",
            details="Unit test details",
        )
        assert log.id is not None
        assert log.action == "TEST_ACTION"

        recent = repo.get_recent_events(org_id="test_org", limit=5)
        assert len(recent) >= 1
        assert any(l.action == "TEST_ACTION" for l in recent)


def test_customer_repository_operations():
    with db_session_scope() as session:
        repo = CustomerRepository(session)
        
        # Upsert or retrieve test customer
        existing = repo.get_by_customer_id("cust_test_db", org_id="test_org")
        if not existing:
            cust = Customer(
                customer_id="cust_test_db",
                org_id="test_org",
                city="Sao Paulo",
                state="SP",
                rfm_segment="Champions",
                total_spend=1500.0,
                total_orders=4,
                recency_days=20,
                churn_probability=0.10,
                predicted_clv=950.0,
            )
            repo.add(cust)
            repo.commit()

        retrieved = repo.get_by_customer_id("cust_test_db", org_id="test_org")
        assert retrieved is not None
        assert retrieved.total_spend == 1500.0

        results, count = repo.search_and_filter(org_id="test_org", segment="Champions")
        assert count >= 1
        assert any(c.customer_id == "cust_test_db" for c in results)
