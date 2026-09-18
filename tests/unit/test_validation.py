"""Unit tests for schema and data validation utilities."""

import pandas as pd
import pytest
from utils.validation import validate_customer_dataframe, validate_customer_id


def test_validate_customer_dataframe_valid(sample_customer_df: pd.DataFrame):
    valid, issues = validate_customer_dataframe(sample_customer_df)
    assert valid is True
    assert len(issues) == 0


def test_validate_customer_dataframe_empty(empty_customer_df: pd.DataFrame):
    valid, issues = validate_customer_dataframe(empty_customer_df)
    assert valid is False
    assert any("empty" in i.lower() for i in issues)


def test_validate_customer_dataframe_missing_column(sample_customer_df: pd.DataFrame):
    corrupt_df = sample_customer_df.drop(columns=["customer_id"])
    valid, issues = validate_customer_dataframe(corrupt_df)
    assert valid is False
    assert any("missing" in i.lower() for i in issues)


def test_validate_customer_dataframe_negative_spend(sample_customer_df: pd.DataFrame):
    corrupt_df = sample_customer_df.copy()
    corrupt_df.loc[0, "total_spend"] = -50.0
    valid, issues = validate_customer_dataframe(corrupt_df)
    assert valid is False
    assert any("negative" in i.lower() for i in issues)


def test_validate_customer_dataframe_invalid_churn(sample_customer_df: pd.DataFrame):
    corrupt_df = sample_customer_df.copy()
    corrupt_df.loc[0, "churn_probability"] = 1.5
    valid, issues = validate_customer_dataframe(corrupt_df)
    assert valid is False
    assert any("churn" in i.lower() for i in issues)


def test_validate_customer_id(sample_customer_df: pd.DataFrame):
    assert validate_customer_id("cust_001", sample_customer_df) is True
    assert validate_customer_id("non_existent_cust", sample_customer_df) is False
    assert validate_customer_id(None, sample_customer_df) is False
