"""Tests for relational database repositories."""

import pytest
from database.connection import init_db, db_session_scope
from database.models import Organization, Customer
from database.repositories.customer_repository import CustomerRepository
from database.repositories.analytics_repository import AnalyticsRepository


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db()


def test_customer_repository_crud():
    with db_session_scope() as session:
        # Create test customer
        cust_repo = CustomerRepository(session)
        test_cust = Customer(
            customer_id="cust_db_test_01",
            org_id="default_org",
            city="sao paulo",
            state="SP",
            rfm_segment="Champions",
            total_spend=1500.0,
            total_orders=3,
            predicted_clv=600.0,
            churn_probability=0.20,
        )
        session.merge(test_cust)
        session.flush()

        # Query by ID
        fetched = cust_repo.get_by_customer_id("cust_db_test_01")
        assert fetched is not None
        assert fetched.customer_id == "cust_db_test_01"
        assert fetched.rfm_segment == "Champions"

        # Search & Filter
        results, count = cust_repo.search_and_filter(search_query="db_test")
        assert count >= 1
        assert any(c.customer_id == "cust_db_test_01" for c in results)


def test_analytics_repository_overview():
    with db_session_scope() as session:
        analytics_repo = AnalyticsRepository(session)
        overview = analytics_repo.get_portfolio_overview()
        assert "total_customers" in overview
        assert "total_gmv" in overview
