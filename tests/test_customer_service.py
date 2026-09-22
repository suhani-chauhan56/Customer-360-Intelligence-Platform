"""Unit tests for Customer Domain Service in CustomerAtlas."""

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


def test_get_customer_profile_found(sample_customer_df: pd.DataFrame):
    profile = get_customer_profile(sample_customer_df, "cust_001")
    assert profile is not None
    assert profile["customer_id"] == "cust_001"
    assert profile["total_orders"] == 3


def test_get_customer_profile_not_found(sample_customer_df: pd.DataFrame):
    profile = get_customer_profile(sample_customer_df, "cust_999")
    assert profile is None


def test_get_customer_profile_empty_df(empty_customer_df: pd.DataFrame):
    profile = get_customer_profile(empty_customer_df, "cust_001")
    assert profile is None


def test_search_customers_all(sample_customer_df: pd.DataFrame):
    res = search_customers(sample_customer_df)
    assert len(res) == len(sample_customer_df)


def test_search_customers_query(sample_customer_df: pd.DataFrame):
    res = search_customers(sample_customer_df, search_query="paulo")
    assert len(res) == 1
    assert res.iloc[0]["customer_id"] == "cust_001"


def test_search_customers_segment(sample_customer_df: pd.DataFrame):
    res = search_customers(sample_customer_df, segment="Champions")
    assert len(res) == 1
    assert res.iloc[0]["rfm_segment"] == "Champions"


def test_search_customers_risk_filter(sample_customer_df: pd.DataFrame):
    res_high = search_customers(sample_customer_df, risk_level="High Risk (>=65%)")
    assert len(res_high) == 1
    assert res_high.iloc[0]["customer_id"] == "cust_002"


def test_compute_customer_health(single_customer_profile: pd.Series):
    vitals = compute_customer_health(single_customer_profile)
    assert len(vitals) == 6
    dimensions = [v["dimension"] for v in vitals]
    assert "Purchase Recency" in dimensions
    assert "Order Frequency" in dimensions
    assert "Monetary Value" in dimensions
    assert "Digital Engagement" in dimensions
    assert "Feedback & CSAT" in dimensions
    assert "Retention Health" in dimensions


def test_derive_lifecycle_stages(single_customer_profile: pd.Series):
    stages = derive_lifecycle_stages(single_customer_profile)
    assert len(stages) == 5
    assert stages[0]["stage"] == "First Purchase"
    assert stages[0]["reached"] is True


def test_diagnose_customer_risk_factors(single_customer_profile: pd.Series):
    diag = diagnose_customer_risk_factors(single_customer_profile)
    assert "risk_level" in diag
    assert "churn_probability" in diag
    assert "risk_factors" in diag
    assert "protective_factors" in diag
    assert diag["risk_level"] == "Low Risk"


def test_explain_rfm_segment(single_customer_profile: pd.Series):
    rfm_exp = explain_rfm_segment(single_customer_profile)
    assert rfm_exp["segment"] == "Champions"
    assert "R:5 | F:4 | M:5" in rfm_exp["rfm_code"]
    assert len(rfm_exp["factors"]) == 3
