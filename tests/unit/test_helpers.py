"""Unit tests for defensive helper utilities."""

import pandas as pd
import pytest
from utils.helpers import (
    calculate_data_snapshot_info,
    calculate_pareto_cutoff,
    safe_float,
    safe_int,
    safe_str,
)


def test_safe_conversions():
    assert safe_float("123.45") == 123.45
    assert safe_float(None, default=0.0) == 0.0
    assert safe_float("invalid", default=-1.0) == -1.0

    assert safe_int("42") == 42
    assert safe_int(42.8) == 42
    assert safe_int(None, default=0) == 0

    assert safe_str(123) == "123"
    assert safe_str(" hello ") == "hello"
    assert safe_str(None, default="N/A") == "N/A"


def test_calculate_pareto_cutoff():
    s = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    cutoff = calculate_pareto_cutoff(s, top_pct=0.20)
    assert cutoff >= 80.0
    assert calculate_pareto_cutoff(pd.Series([])) == 0.0


def test_calculate_data_snapshot_info(sample_customer_df: pd.DataFrame):
    info = calculate_data_snapshot_info(sample_customer_df)
    assert info["rows"] == 3
    assert info["columns"] > 10
    assert info["has_records"] is True
    assert info["memory_mb"] >= 0.0
