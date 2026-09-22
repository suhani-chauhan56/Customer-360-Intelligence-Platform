"""Unit tests for Customer Health Score and Lifecycle State Machine in CustomerAtlas."""

import pandas as pd
import pytest
from services.health_score_service import (
    calculate_customer_health_score,
    classify_lifecycle_state,
)


def test_calculate_customer_health_score(single_customer_profile: pd.Series):
    health = calculate_customer_health_score(single_customer_profile)
    assert "score" in health
    assert 0.0 <= health["score"] <= 100.0
    assert "health_tier" in health
    assert "components" in health
    assert len(health["components"]) == 6
    assert health.total_score == health["score"]
    assert health.grade == health["health_tier"]


def test_classify_lifecycle_state(single_customer_profile: pd.Series):
    lifecycle = classify_lifecycle_state(single_customer_profile)
    assert "lifecycle_state" in lifecycle
    assert lifecycle["lifecycle_state"] in [
        "New",
        "Activated",
        "Engaged",
        "Loyal",
        "At Risk",
        "Inactive / Lost",
    ]
    assert lifecycle.value == lifecycle["lifecycle_state"]
