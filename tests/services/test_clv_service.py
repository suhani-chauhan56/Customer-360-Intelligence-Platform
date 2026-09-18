"""Tests for Customer Lifetime Value (CLV) service."""

import pandas as pd
import pytest
from services.clv_service import (
    analyze_high_value_cohort,
    compute_clv_bins,
    compute_clv_overview,
)


def test_compute_clv_overview(sample_customer_df: pd.DataFrame):
    overview = compute_clv_overview(sample_customer_df)
    assert overview["total_customers"] == 3
    assert overview["avg_clv"] > 0
    assert overview["total_pipeline_clv"] > 0


def test_compute_clv_bins(sample_customer_df: pd.DataFrame):
    bins_df = compute_clv_bins(sample_customer_df)
    assert not bins_df.empty
    assert "clv_bracket" in bins_df.columns
    assert "customers" in bins_df.columns
    assert "total_predicted_clv" in bins_df.columns


def test_analyze_high_value_cohort(sample_customer_df: pd.DataFrame):
    hv = analyze_high_value_cohort(sample_customer_df, percentile=0.50)
    assert hv["count"] > 0
    assert hv["revenue_contribution"] > 0
    assert "cohort_df" in hv
    assert not hv["cohort_df"].empty
