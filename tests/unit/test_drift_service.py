"""Unit tests for feature drift monitoring and PSI calculations."""

import numpy as np
import pandas as pd
import pytest
from services.drift_service import calculate_psi, run_feature_drift_audit


def test_calculate_psi_identical():
    s1 = pd.Series(np.random.normal(100, 15, 1000))
    s2 = s1.copy()
    psi = calculate_psi(s1, s2)
    assert psi == 0.0 or psi < 0.05


def test_calculate_psi_shifted():
    s1 = pd.Series(np.random.normal(100, 15, 1000))
    s2 = pd.Series(np.random.normal(180, 15, 1000))  # Significant shift
    psi = calculate_psi(s1, s2)
    assert psi > 0.10


def test_run_feature_drift_audit(sample_customer_df: pd.DataFrame):
    report = run_feature_drift_audit(sample_customer_df, sample_customer_df)
    assert "overall_status" in report
    assert "features" in report
    assert len(report["features"]) > 0
