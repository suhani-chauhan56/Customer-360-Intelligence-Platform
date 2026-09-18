"""Unit tests for configuration and threshold settings."""

import pytest
from config.settings import (
    APP_NAME,
    APP_VERSION,
    APP_ENV,
    DATA_DIR,
    MODELS_DIR,
    CURRENCY_CODE,
    get_environment_info,
)
from config.thresholds import (
    CHURN_THRESHOLD_LOW_MAX,
    CHURN_THRESHOLD_HIGH_MIN,
    RECENCY_DAYS_ACTIVE,
    CLV_P90_PERCENTILE,
)
from config.business_rules import get_retention_playbook, SEGMENT_RULES


def test_settings_initialization():
    assert APP_NAME == "CustomerAtlas"
    assert "2.0" in APP_VERSION
    assert CURRENCY_CODE == "BRL"
    env_info = get_environment_info()
    assert env_info["app_name"] == APP_NAME
    assert "environment" in env_info


def test_threshold_ranges():
    assert 0.0 < CHURN_THRESHOLD_LOW_MAX < CHURN_THRESHOLD_HIGH_MIN < 1.0
    assert RECENCY_DAYS_ACTIVE > 0
    assert CLV_P90_PERCENTILE == 0.90


def test_retention_playbook_logic():
    high_risk_act = get_retention_playbook(0.75, "Champions")
    assert high_risk_act["tier"] == "Critical Priority"

    med_risk_act = get_retention_playbook(0.45, "Regular Customers")
    assert med_risk_act["tier"] == "Moderate Risk"

    champ_act = get_retention_playbook(0.20, "Champions")
    assert champ_act["tier"] == "Advocate / Protect"

    assert "Champions" in SEGMENT_RULES
    assert "Lost Customers" in SEGMENT_RULES
