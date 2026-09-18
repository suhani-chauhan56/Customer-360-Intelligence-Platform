"""Tests for Data Quality & System Health audit service."""

import pandas as pd
import pytest
from services.data_quality_service import run_data_quality_audit


def test_data_quality_audit_healthy(sample_customer_df: pd.DataFrame):
    audit = run_data_quality_audit(sample_customer_df)
    assert audit["is_healthy"] is True
    assert audit["quality_score_pct"] == 100.0
    assert audit["duplicate_customer_ids"] == 0
    assert audit["negative_spend_records"] == 0


def test_data_quality_audit_corrupt(sample_customer_df: pd.DataFrame):
    corrupt_df = sample_customer_df.copy()
    corrupt_df.loc[0, "total_spend"] = -100.0
    corrupt_df.loc[1, "churn_probability"] = 2.5

    audit = run_data_quality_audit(corrupt_df)
    assert audit["is_healthy"] is False
    assert audit["quality_score_pct"] < 100.0
    assert audit["negative_spend_records"] == 1
    assert audit["invalid_churn_probabilities"] == 1
