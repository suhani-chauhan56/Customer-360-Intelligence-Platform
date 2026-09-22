"""Integration tests for CustomerAtlas FastAPI REST API."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from security.auth import MASTER_API_KEY


@pytest.fixture
def client():
    return TestClient(app)


def test_api_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "CustomerAtlas"
    assert data["status"] == "Operational 🟢"


def test_system_health(client: TestClient):
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]


def test_list_segments(client: TestClient):
    response = client.get(
        "/api/v1/segments",
        headers={"X-API-Key": MASTER_API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_portfolio_overview(client: TestClient):
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"X-API-Key": MASTER_API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_customers" in data["data"]
    assert "total_gmv" in data["data"]


def test_ask_customer_atlas(client: TestClient):
    response = client.post(
        "/api/v1/analytics/ask",
        json={"query": "Which customers are high-value and high-risk?"},
        headers={"X-API-Key": MASTER_API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["intent"] == "high_value_high_risk"
    assert data["data"]["headline"] != ""


def test_model_registry(client: TestClient):
    response = client.get(
        "/api/v1/ml/models",
        headers={"X-API-Key": MASTER_API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_predict_churn_endpoint(client: TestClient):
    payload = {
        "recency_days": 120.0,
        "frequency": 1.0,
        "monetary": 89.9,
        "avg_order_value": 89.9,
        "number_of_products": 1.0,
        "customer_age_days": 120.0,
    }
    response = client.post(
        "/api/v1/ml/predict/churn",
        json=payload,
        headers={"X-API-Key": MASTER_API_KEY},
    )
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "churn_probability" in data["data"]


def test_unauthorized_access(client: TestClient):
    response = client.get(
        "/api/v1/system/audit-logs",
        headers={"X-API-Key": "invalid_wrong_key"},
    )
    assert response.status_code == 401
