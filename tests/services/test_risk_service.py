"""Tests for churn risk and customer prioritization service."""

import pandas as pd
import pytest
from services.risk_service import (
    calculate_customer_prioritization,
    compute_quadrant_matrix,
    compute_risk_distribution,
    compute_risk_overview,
)


def test_compute_risk_overview(sample_customer_df: pd.DataFrame):
    risk_info = compute_risk_overview(sample_customer_df)
    assert risk_info["total_customers"] == 3
    assert risk_info["at_risk_count"] == 1  # cust_002 has 0.78 churn prob
    assert risk_info["at_risk_revenue"] > 0


def test_compute_risk_distribution(sample_customer_df: pd.DataFrame):
    risk_dist = compute_risk_distribution(sample_customer_df)
    assert not risk_dist.empty
    assert "risk_tier" in risk_dist.columns
    assert "customers" in risk_dist.columns


def test_calculate_customer_prioritization(sample_customer_df: pd.DataFrame):
    prio_df = calculate_customer_prioritization(sample_customer_df, top_n=10)
    assert not prio_df.empty
    assert "priority_score" in prio_df.columns
    assert prio_df["priority_score"].iloc[0] >= prio_df["priority_score"].iloc[-1]


def test_compute_quadrant_matrix(sample_customer_df: pd.DataFrame):
    quad = compute_quadrant_matrix(sample_customer_df)
    assert "quadrants" in quad
    assert len(quad["quadrants"]) == 4
