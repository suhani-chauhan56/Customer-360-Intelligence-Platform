"""Integration tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
AUTH_HEADERS = {
    "X-API-Key": "ca_live_enterprise_secret_key_demo",
    "X-Organization-ID": "default_org",
}


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["application"] == "CustomerAtlas"
    assert "documentation" in json_data


def test_get_system_health():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "status" in json_data["data"]


def test_get_analytics_overview():
    response = client.get("/api/v1/analytics/overview", headers=AUTH_HEADERS)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "total_customers" in json_data["data"]
    assert "total_gmv" in json_data["data"]


def test_get_segments():
    response = client.get("/api/v1/segments", headers=AUTH_HEADERS)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) > 0


def test_list_customers():
    response = client.get("/api/v1/customers?page=1&page_size=10", headers=AUTH_HEADERS)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["items"]) <= 10
    assert "pagination" in json_data


def test_get_customer_360():
    # Fetch customer ID from list
    list_res = client.get("/api/v1/customers?page=1&page_size=1", headers=AUTH_HEADERS)
    assert list_res.status_code == 200
    cid = list_res.json()["items"][0]["customer_id"]

    res_360 = client.get(f"/api/v1/customers/{cid}/360", headers=AUTH_HEADERS)
    assert res_360.status_code == 200
    data_360 = res_360.json()["data"]
    assert data_360["customer_id"] == cid
    assert "health_vitals" in data_360
    assert "health_score" in data_360
    assert "lifecycle_state" in data_360


def test_simulate_customer_scenario():
    list_res = client.get("/api/v1/customers?page=1&page_size=1", headers=AUTH_HEADERS)
    cid = list_res.json()["items"][0]["customer_id"]

    sim_res = client.post(
        f"/api/v1/customers/{cid}/simulate",
        json={"additional_orders": 2, "aov_multiplier": 1.25, "recency_reduction_days": 60},
        headers=AUTH_HEADERS,
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()["data"]
    assert "delta" in sim_data
    assert "disclaimer" in sim_data


def test_predict_churn_endpoint():
    payload = {
        "recency_days": 120,
        "frequency": 2,
        "monetary": 350.0,
        "avg_order_value": 175.0,
        "number_of_products": 2,
        "customer_age_days": 90,
    }
    res = client.post("/api/v1/ml/predict/churn", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    pred = res.json()["data"]
    assert "churn_probability" in pred
    assert 0.0 <= pred["churn_probability"] <= 1.0


def test_predict_clv_endpoint():
    payload = {
        "recency_days": 45,
        "frequency": 3,
        "monetary": 600.0,
        "avg_order_value": 200.0,
        "number_of_products": 3,
        "customer_age_days": 120,
    }
    res = client.post("/api/v1/ml/predict/clv", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    pred = res.json()["data"]
    assert "predicted_12m_clv" in pred
    assert pred["predicted_12m_clv"] >= 0.0


def test_get_audit_logs():
    res = client.get("/api/v1/system/audit-logs", headers=AUTH_HEADERS)
    assert res.status_code == 200
    logs = res.json()["data"]
    assert isinstance(logs, list)
