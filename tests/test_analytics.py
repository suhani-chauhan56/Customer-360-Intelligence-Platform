"""Unit tests for root analytics.py and src package."""

import pandas as pd
import pytest
from analytics import (
    calculate_health_score,
    calculate_population_stability_index,
    classify_lifecycle_stage,
    compute_clv_brackets,
    compute_executive_kpis,
    compute_rfm_distribution,
    load_dataset,
    prioritize_retention_queue,
    run_full_analytics_audit,
    validate_dataset,
)
from src.data_loader import DataLoader
from src.preprocessing import clean_customer_features, derive_rfm_scores


def test_compute_executive_kpis(sample_customer_df: pd.DataFrame):
    kpis = compute_executive_kpis(sample_customer_df)
    assert kpis.total_customers == 3
    assert kpis.total_gmv > 0
    assert kpis.active_customers >= 1
    assert kpis.at_risk_customers_count == 1
    assert kpis.repeat_customers_count == 2


def test_compute_rfm_distribution(sample_customer_df: pd.DataFrame):
    dist = compute_rfm_distribution(sample_customer_df)
    assert not dist.empty
    assert "rfm_segment" in dist.columns
    assert "customer_share" in dist.columns
    assert "revenue_share" in dist.columns


def test_compute_clv_brackets(sample_customer_df: pd.DataFrame):
    brackets = compute_clv_brackets(sample_customer_df)
    assert not brackets.empty
    assert "clv_bracket" in brackets.columns
    assert "customers" in brackets.columns


def test_prioritize_retention_queue(sample_customer_df: pd.DataFrame):
    queue = prioritize_retention_queue(sample_customer_df, top_n=5)
    assert not queue.empty
    assert "priority_score" in queue.columns
    assert len(queue) <= 3


def test_calculate_health_score(single_customer_profile: pd.Series):
    health = calculate_health_score(single_customer_profile)
    assert "score" in health
    assert 0.0 <= health["score"] <= 100.0
    assert "health_tier" in health
    assert "components" in health


def test_classify_lifecycle_stage(single_customer_profile: pd.Series):
    lifecycle = classify_lifecycle_stage(single_customer_profile)
    assert "lifecycle_state" in lifecycle
    assert lifecycle["lifecycle_state"] in ["New", "Activated", "Engaged", "Loyal", "At Risk", "Inactive / Lost"]


def test_calculate_population_stability_index():
    s1 = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0] * 100)
    s2 = pd.Series([1.1, 2.0, 3.1, 4.0, 5.1] * 100)
    psi = calculate_population_stability_index(s1, s2)
    assert psi >= 0.0
    assert psi < 0.10


def test_run_full_analytics_audit(sample_customer_df: pd.DataFrame):
    audit = run_full_analytics_audit(sample_customer_df)
    assert audit["status"] == "Success"
    assert "data_validation" in audit
    assert "executive_kpis" in audit


def test_data_loader_and_preprocessing(sample_customer_df: pd.DataFrame):
    loader = DataLoader()
    assert loader.validate(sample_customer_df) is True

    cleaned = clean_customer_features(sample_customer_df)
    assert len(cleaned) == len(sample_customer_df)

    scored = derive_rfm_scores(sample_customer_df)
    assert "r_score" in scored.columns
    assert "f_score" in scored.columns
    assert "m_score" in scored.columns
    assert "rfm_score" in scored.columns


def test_overview_cohort_calculations(sample_customer_df: pd.DataFrame):
    df = sample_customer_df
    total_customers = df["customer_id"].nunique()

    healthy_cohorts = ["Champions", "Loyal Customers", "Potential Loyalists"]
    h_count = int(df[df["rfm_segment"].isin(healthy_cohorts)]["customer_id"].count())
    h_rev = float(df[df["rfm_segment"].isin(healthy_cohorts)]["total_spend"].sum())
    h_pct = h_count / max(1, total_customers)

    reg_count = int(df[df["rfm_segment"] == "Regular Customers"]["customer_id"].count())
    reg_rev = float(df[df["rfm_segment"] == "Regular Customers"]["total_spend"].sum())
    reg_pct = reg_count / max(1, total_customers)

    risk_cohort_count = int(df[df["rfm_segment"] == "At Risk"]["customer_id"].count())
    risk_cohort_rev = float(df[df["rfm_segment"] == "At Risk"]["total_spend"].sum())
    risk_cohort_pct = risk_cohort_count / max(1, total_customers)

    lost_cohort_count = int(df[df["rfm_segment"] == "Lost Customers"]["customer_id"].count())
    lost_cohort_rev = float(df[df["rfm_segment"] == "Lost Customers"]["total_spend"].sum())
    lost_cohort_pct = lost_cohort_count / max(1, total_customers)

    assert total_customers > 0
    assert h_count + reg_count + risk_cohort_count + lost_cohort_count <= total_customers
    assert 0.0 <= lost_cohort_pct <= 1.0
    assert lost_cohort_count >= 0
    assert lost_cohort_rev >= 0.0

