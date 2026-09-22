"""Unit tests for Feature Drift Monitoring and Data Quality Audits."""

import numpy as np
import pandas as pd
import pytest
from services.data_quality_service import run_data_quality_audit
from services.drift_service import calculate_psi, run_feature_drift_audit


def test_calculate_psi_identical_series():
    series = pd.Series(np.random.normal(100, 15, 1000))
    psi = calculate_psi(series, series)
    assert psi < 0.05


def test_calculate_psi_shifted_series():
    baseline = pd.Series(np.random.normal(100, 15, 1000))
    shifted = pd.Series(np.random.normal(150, 15, 1000))
    psi = calculate_psi(baseline, shifted)
    assert psi > 0.10


def test_run_feature_drift_audit(sample_customer_df: pd.DataFrame):
    report = run_feature_drift_audit(sample_customer_df, sample_customer_df)
    assert "overall_status" in report
    assert "features" in report
    assert report["drift_detected"] is False


def test_run_data_quality_audit(sample_customer_df: pd.DataFrame):
    audit = run_data_quality_audit(sample_customer_df)
    assert "is_healthy" in audit
    assert "quality_score_pct" in audit
    assert audit["total_records"] == len(sample_customer_df)
    assert audit["null_customer_ids"] == 0
    assert audit["negative_spend_records"] == 0
