"""Tests for customer domain service functions."""

import pandas as pd
import pytest
from services.customer_service import (
    compute_customer_health,
    derive_lifecycle_stages,
    diagnose_customer_risk_factors,
    explain_rfm_segment,
    get_customer_profile,
    search_customers,
)


def test_get_customer_profile(sample_customer_df: pd.DataFrame):
    prof = get_customer_profile(sample_customer_df, "cust_001")
    assert prof is not None
    assert prof["customer_id"] == "cust_001"
    assert prof["rfm_segment"] == "Champions"

    missing = get_customer_profile(sample_customer_df, "nonexistent")
    assert missing is None


def test_search_customers_query(sample_customer_df: pd.DataFrame):
    # Search by ID
    res = search_customers(sample_customer_df, search_query="cust_001")
    assert len(res) == 1
    assert res.iloc[0]["customer_id"] == "cust_001"

    # Search by city
    res_city = search_customers(sample_customer_df, search_query="sao paulo")
    assert len(res_city) == 1


def test_search_customers_filters(sample_customer_df: pd.DataFrame):
    # Segment filter
    res_seg = search_customers(sample_customer_df, segment="Champions")
    assert len(res_seg) == 1
    assert res_seg.iloc[0]["customer_id"] == "cust_001"

    # Risk filter
    res_risk = search_customers(sample_customer_df, risk_level="High Risk (>=65%)")
    assert len(res_risk) == 1
    assert res_risk.iloc[0]["customer_id"] == "cust_002"

    # State filter
    res_state = search_customers(sample_customer_df, state="SP")
    assert len(res_state) == 1


def test_compute_customer_health(single_customer_profile: pd.Series):
    health = compute_customer_health(single_customer_profile)
    assert len(health) == 6
    dims = [h["dimension"] for h in health]
    assert "Purchase Recency" in dims
    assert "Order Frequency" in dims
    assert "Monetary Value" in dims
    assert "Feedback & CSAT" in dims


def test_derive_lifecycle_stages(single_customer_profile: pd.Series):
    stages = derive_lifecycle_stages(single_customer_profile)
    assert len(stages) == 5
    assert stages[0]["stage"] == "First Purchase"
    assert stages[0]["reached"] is True


def test_diagnose_customer_risk_factors(single_customer_profile: pd.Series):
    diag = diagnose_customer_risk_factors(single_customer_profile)
    assert "risk_level" in diag
    assert "risk_factors" in diag
    assert "protective_factors" in diag
    assert diag["risk_level"] == "Low Risk"


def test_explain_rfm_segment(single_customer_profile: pd.Series):
    exp = explain_rfm_segment(single_customer_profile)
    assert exp["segment"] == "Champions"
    assert len(exp["factors"]) == 3
