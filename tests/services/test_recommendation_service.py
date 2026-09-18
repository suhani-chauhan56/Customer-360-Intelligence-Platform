"""Tests for recommendation domain service."""

import pandas as pd
import pytest
from services.recommendation_service import (
    get_customer_recommendations,
    summarize_recommendation_methods,
)


@pytest.fixture
def sample_recs_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"customer_id": "cust_001", "rank": 1, "recommended_category": "perfumery", "reason": "Frequent basket pairing", "method": "Basket Co-occurrence"},
        {"customer_id": "cust_001", "rank": 2, "recommended_category": "beauty", "reason": "Category affinity", "method": "Basket Co-occurrence"},
        {"customer_id": "cust_002", "rank": 1, "recommended_category": "housewares", "reason": "Seasonal trend", "method": "Popularity Fallback"},
    ])


def test_get_customer_recommendations(sample_recs_df: pd.DataFrame):
    recs = get_customer_recommendations(sample_recs_df, "cust_001", top_n=5)
    assert len(recs) == 2
    assert recs[0]["rank"] == 1
    assert recs[0]["recommended_category"] == "perfumery"

    missing = get_customer_recommendations(sample_recs_df, "unknown_cust")
    assert len(missing) == 0


def test_summarize_recommendation_methods(sample_recs_df: pd.DataFrame):
    summary = summarize_recommendation_methods(sample_recs_df)
    assert not summary.empty
    assert "Recommendation Method" in summary.columns
    assert "Volume" in summary.columns
