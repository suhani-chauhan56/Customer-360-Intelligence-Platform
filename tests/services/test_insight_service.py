"""Tests for structured business insight service."""

import pandas as pd
import pytest
from services.insight_service import generate_executive_insights


def test_generate_executive_insights(sample_customer_df: pd.DataFrame):
    insights = generate_executive_insights(sample_customer_df)
    assert len(insights) >= 3
    for ins in insights:
        assert "title" in ins
        assert "observation" in ins
        assert "evidence" in ins
        assert "implication" in ins
        assert "badge" in ins


def test_generate_executive_insights_empty(empty_customer_df: pd.DataFrame):
    insights = generate_executive_insights(empty_customer_df)
    assert len(insights) == 0
