"""Unit tests for Risk and Churn Intelligence Service in CustomerAtlas."""

import pandas as pd
import pytest
from services.risk_service import (
    calculate_customer_prioritization,
    compute_quadrant_matrix,
    compute_risk_distribution,
    compute_risk_overview,
)


def test_compute_risk_overview(sample_customer_df: pd.DataFrame):
    overview = compute_risk_overview(sample_customer_df)
    assert overview["total_customers"] == 3
    assert overview["at_risk_count"] == 1  # cust_002 has 0.78 churn_prob
    assert overview["at_risk_revenue"] == 89.90


def test_compute_risk_distribution(sample_customer_df: pd.DataFrame):
    dist = compute_risk_distribution(sample_customer_df)
    assert not dist.empty
    assert "risk_tier" in dist.columns
    assert "customers" in dist.columns


def test_calculate_customer_prioritization(sample_customer_df: pd.DataFrame):
    prio_df = calculate_customer_prioritization(sample_customer_df, top_n=10)
    assert not prio_df.empty
    assert "priority_score" in prio_df.columns
    # Check that priority scores are sorted descending
    scores = prio_df["priority_score"].tolist()
    assert scores == sorted(scores, reverse=True)


def test_compute_quadrant_matrix(sample_customer_df: pd.DataFrame):
    quad = compute_quadrant_matrix(sample_customer_df)
    assert "quadrants" in quad
    assert len(quad["quadrants"]) == 4
    assert "Priority Protect (High Value, High Risk)" in quad["quadrants"]
