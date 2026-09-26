"""Comprehensive test suite for CustomerAtlas Domain Services."""

import pandas as pd
import pytest

from services.customer_service import (
    compute_customer_health,
    derive_lifecycle_stages,
    diagnose_customer_risk_factors,
    explain_rfm_segment,
    get_customer_profile,
    search_customers,
)
from services.clv_service import (
    analyze_high_value_cohort,
    compute_clv_bins,
    compute_clv_overview,
)
from services.data_quality_service import run_data_quality_audit
from services.drift_service import calculate_psi, run_feature_drift_audit
from services.health_score_service import calculate_customer_health_score, classify_lifecycle_state
from services.recommendation_service import (
    RECOMMENDATION_RULES,
    compute_recommendation_portfolio,
    compute_recommendation_summary,
    generate_customer_recommendation,
)
from services.rfm_service import (
    compare_segments,
    compute_rfm_overview,
    compute_segment_distribution,
    get_segment_playbook,
)
from services.risk_service import (
    calculate_customer_prioritization,
    compute_quadrant_matrix,
    compute_risk_distribution,
    compute_risk_overview,
)
from services.sentiment_service import (
    compute_sentiment_overview,
    compute_sentiment_trend,
    extract_negative_themes,
)


def test_customer_service_profile_and_search(sample_customer_df: pd.DataFrame):
    # Lookup profile
    prof = get_customer_profile(sample_customer_df, "cust_001")
    assert prof is not None
    assert prof["customer_id"] == "cust_001"

    # Search with keyword
    found = search_customers(sample_customer_df, search_query="sao paulo")
    assert len(found) == 1
    assert found.iloc[0]["customer_id"] == "cust_001"

    # Search with segment filter
    champs = search_customers(sample_customer_df, segment="Champions")
    assert len(champs) == 1

    # Empty lookup
    assert get_customer_profile(sample_customer_df, "non_existent_id") is None
    assert search_customers(pd.DataFrame()).empty


def test_customer_health_and_diagnostics(single_customer_profile: pd.Series):
    vitals = compute_customer_health(single_customer_profile)
    assert len(vitals) == 6
    assert all("dimension" in v and "rating" in v and "color" in v for v in vitals)

    diag = diagnose_customer_risk_factors(single_customer_profile)
    assert "risk_level" in diag
    assert "churn_probability" in diag
    assert isinstance(diag["risk_factors"], list)

    stages = derive_lifecycle_stages(single_customer_profile)
    assert len(stages) >= 4

    rfm_exp = explain_rfm_segment(single_customer_profile)
    assert "segment" in rfm_exp
    assert "factors" in rfm_exp


def test_rfm_service(sample_customer_df: pd.DataFrame):
    overview = compute_rfm_overview(sample_customer_df)
    assert overview["total_customers"] == 3
    assert overview["avg_recency"] > 0
    assert overview["avg_frequency"] > 0

    dist = compute_segment_distribution(sample_customer_df)
    assert not dist.empty
    assert "customers" in dist.columns
    assert "customer_share" in dist.columns

    comp = compare_segments(sample_customer_df, "Champions", "Lost Customers")
    assert len(comp) > 0

    playbook = get_segment_playbook("Champions")
    assert "title" in playbook
    assert "actions" in playbook


def test_clv_service(sample_customer_df: pd.DataFrame):
    overview = compute_clv_overview(sample_customer_df)
    assert overview["total_customers"] == 3
    assert overview["avg_clv"] > 0
    assert overview["total_pipeline_clv"] > 0

    bins = compute_clv_bins(sample_customer_df)
    assert not bins.empty

    high_val = analyze_high_value_cohort(sample_customer_df, percentile=0.50)
    assert high_val["count"] >= 1
    assert "threshold" in high_val


def test_risk_service(sample_customer_df: pd.DataFrame):
    overview = compute_risk_overview(sample_customer_df)
    assert overview["total_customers"] == 3
    assert overview["at_risk_count"] == 1
    assert overview["at_risk_revenue"] == 89.90

    dist = compute_risk_distribution(sample_customer_df)
    assert not dist.empty

    prio = calculate_customer_prioritization(sample_customer_df)
    assert not prio.empty
    assert "priority_score" in prio.columns
    assert "avg_order_value" in prio.columns
    assert "clv_band" in prio.columns

    # Test edge case with missing AOV and zero orders
    edge_df = pd.DataFrame([
        {"customer_id": "c1", "total_spend": 0.0, "total_orders": 0, "predicted_clv": 50.0, "churn_probability": 0.8},
        {"customer_id": "c2", "total_spend": 100.0, "total_orders": 2, "predicted_clv": 150.0, "churn_probability": 0.3},
    ])
    prio_edge = calculate_customer_prioritization(edge_df)
    assert "avg_order_value" in prio_edge.columns
    assert prio_edge.loc[prio_edge["customer_id"] == "c1", "avg_order_value"].iloc[0] == 0.0
    assert prio_edge.loc[prio_edge["customer_id"] == "c2", "avg_order_value"].iloc[0] == 50.0

    quad = compute_quadrant_matrix(sample_customer_df)
    assert "quadrants" in quad
    assert len(quad["quadrants"]) == 4


def test_recommendation_service(sample_customer_df: pd.DataFrame, single_customer_profile: pd.Series):
    rec = generate_customer_recommendation(single_customer_profile)
    assert "action_type" in rec
    assert "priority" in rec
    assert "reason" in rec

    portfolio = compute_recommendation_portfolio(sample_customer_df)
    assert len(portfolio) == 3
    assert "avg_order_value" in portfolio.columns
    assert "total_orders" in portfolio.columns
    assert "clv_band" in portfolio.columns

    summary = compute_recommendation_summary(portfolio)
    assert not summary.empty
    assert "customer_count" in summary.columns


def test_sentiment_service():
    mock_reviews = pd.DataFrame([
        {"review_score": 5, "sentiment_category": "Positive", "review_creation_date": pd.Timestamp("2018-01-01"), "review_comment_message": "Excelente produto, chegou rapido.", "review_month": "2018-01"},
        {"review_score": 1, "sentiment_category": "Negative", "review_creation_date": pd.Timestamp("2018-01-15"), "review_comment_message": "Muito atraso na entrega, nunca chegou.", "review_month": "2018-01"},
        {"review_score": 3, "sentiment_category": "Neutral", "review_creation_date": pd.Timestamp("2018-02-01"), "review_comment_message": None, "review_month": "2018-02"},
    ])

    overview = compute_sentiment_overview(mock_reviews)
    assert overview["total_reviews"] == 3
    assert overview["positive_count"] == 1
    assert overview["negative_count"] == 1
    assert overview["neutral_count"] == 1

    trend = compute_sentiment_trend(mock_reviews)
    assert not trend.empty

    themes = extract_negative_themes(mock_reviews)
    assert len(themes) > 0
    assert any("Delay" in t["theme"] for t in themes)


def test_data_quality_service(sample_customer_df: pd.DataFrame):
    audit = run_data_quality_audit(sample_customer_df)
    assert audit["is_healthy"] is True
    assert audit["quality_score_pct"] == 100.0
    assert audit["duplicate_customer_ids"] == 0
    assert audit["null_customer_ids"] == 0


def test_drift_service(sample_customer_df: pd.DataFrame):
    s1 = sample_customer_df["recency_days"]
    s2 = sample_customer_df["recency_days"] + 5
    psi = calculate_psi(s1, s2)
    assert psi >= 0.0

    report = run_feature_drift_audit(sample_customer_df, sample_customer_df)
    assert "features" in report
    assert report["drift_detected"] is False
