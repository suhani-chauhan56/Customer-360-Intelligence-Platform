"""Unit and integration tests for analytics API routes and services."""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from services.insight_service import generate_executive_insights
from services.recommendation_service import get_customer_recommendations


@pytest.fixture
def api_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_generate_executive_insights(sample_customer_df: pd.DataFrame):
    insights = generate_executive_insights(sample_customer_df)
    assert isinstance(insights, list)
    assert len(insights) >= 3

    for ins in insights:
        assert "title" in ins
        assert "observation" in ins
        assert "evidence" in ins
        assert "implication" in ins
        assert "badge" in ins
        assert "kind" in ins


def test_get_customer_recommendations():
    recs_df = pd.DataFrame([
        {
            "customer_id": "cust_001",
            "rank": 1,
            "recommended_category": "health_beauty",
            "reason": "Frequently co-purchased",
            "method": "basket_association",
        },
        {
            "customer_id": "cust_001",
            "rank": 2,
            "recommended_category": "housewares",
            "reason": "Frequently co-purchased",
            "method": "basket_association",
        },
    ])

    recs = get_customer_recommendations(recs_df, "cust_001", top_n=5)
    assert len(recs) == 2
    assert recs[0]["rank"] == 1
    assert recs[0]["recommended_category"] == "health_beauty"

    empty_recs = get_customer_recommendations(recs_df, "nonexistent", top_n=5)
    assert empty_recs == []


def test_api_system_health(api_client: TestClient):
    response = api_client.get("/api/v1/system/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "status" in json_data["data"]


def test_api_analytics_overview(api_client: TestClient):
    response = api_client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "total_customers" in json_data["data"]
    assert "total_gmv" in json_data["data"]


def test_api_analytics_insights(api_client: TestClient):
    response = api_client.get("/api/v1/analytics/insights")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) > 0


def test_api_analytics_ask(api_client: TestClient):
    response = api_client.post(
        "/api/v1/analytics/ask",
        json={"query": "What is our customer health and repeat rate?"},
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "headline" in json_data["data"]
    assert "evidence_points" in json_data["data"]
