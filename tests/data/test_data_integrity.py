"""Data integrity verification tests for processed data artifacts."""

from pathlib import Path
import pandas as pd
import pytest
from config.settings import DATA_DIR
from utils.validation import validate_customer_dataframe
from services.data_quality_service import run_data_quality_audit


def test_customer_features_file_exists():
    path = DATA_DIR / "customer_360_features.csv"
    assert path.exists(), f"Customer feature store missing at {path}"


def test_customer_features_schema_and_quality():
    path = DATA_DIR / "customer_360_features.csv"
    if path.exists():
        df = pd.read_csv(path, nrows=1000)
        is_valid, issues = validate_customer_dataframe(df)
        assert is_valid is True, f"Schema validation failed on real sample: {issues}"

        audit = run_data_quality_audit(df)
        assert audit["is_healthy"] is True, f"Data quality audit failed on real sample: {audit}"
        assert audit["quality_score_pct"] == 100.0


def test_other_core_artifacts_exist():
    expected_files = [
        "fact_orders.csv",
        "fact_payments.csv",
        "recommendations.csv",
        "segment_summary.csv",
    ]
    for fname in expected_files:
        p = DATA_DIR / fname
        assert p.exists(), f"Expected core data artifact missing: {fname}"
