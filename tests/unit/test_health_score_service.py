"""Unit tests for Customer Health Scoring and Lifecycle state machine."""

import pandas as pd
import pytest
from services.health_score_service import calculate_customer_health_score, classify_lifecycle_state


def test_calculate_customer_health_score_thriving(single_customer_profile: pd.Series):
    health = calculate_customer_health_score(single_customer_profile)
    assert 0.0 <= health["score"] <= 100.0
    assert "health_tier" in health
    assert "components" in health
    assert "Recency Vital" in health["components"]
    assert "Frequency Vital" in health["components"]


def test_calculate_customer_health_score_critical(sample_customer_df: pd.DataFrame):
    lost_cust = sample_customer_df.iloc[1]  # cust_002 with 380d recency and 0.78 churn
    health = calculate_customer_health_score(lost_cust)
    assert health["score"] < 50.0
    assert "Critical" in health["health_tier"] or "Risk" in health["health_tier"]


def test_classify_lifecycle_state(sample_customer_df: pd.DataFrame):
    # Champion -> Loyal
    champ = sample_customer_df.iloc[0]
    st_champ = classify_lifecycle_state(champ)
    assert st_champ["lifecycle_state"] == "Loyal"

    # Inactive -> Inactive / Lost
    lost = sample_customer_df.iloc[1]
    st_lost = classify_lifecycle_state(lost)
    assert st_lost["lifecycle_state"] == "Inactive / Lost"
