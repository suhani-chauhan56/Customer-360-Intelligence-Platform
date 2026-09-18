"""Unit tests for GroundedAIService and Ask CustomerAtlas natural language analytics."""

import pytest
import pandas as pd
import numpy as np

from services.grounded_ai_service import GroundedAIService, GroundedAnswer


@pytest.fixture
def sample_customer_df() -> pd.DataFrame:
    """Provide a fixture DataFrame mimicking customer_360_features.csv."""
    data = {
        "customer_id": [f"cust_{i:04d}" for i in range(100)],
        "total_spend": [100.0 + i * 15.0 for i in range(100)],
        "total_orders": [1 if i < 85 else 2 + (i % 3) for i in range(100)],
        "recency_days": [10 + i * 5 for i in range(100)],
        "predicted_clv": [200.0 + i * 20.0 for i in range(100)],
        "churn_probability": [0.10 + (i * 0.008) for i in range(100)],
        "rfm_segment": [
            "Champions" if i > 80 else "Loyal Customers" if i > 60 else "At Risk" if i > 30 else "Hibernating"
            for i in range(100)
        ],
        "state": ["SP" if i % 2 == 0 else "RJ" if i % 3 == 0 else "MG" for i in range(100)],
        "city": ["São Paulo" if i % 2 == 0 else "Rio de Janeiro" for i in range(100)],
        "favorite_category": ["bed_bath_table" if i % 2 == 0 else "health_beauty" for i in range(100)],
        "number_of_products": [1 + (i % 4) for i in range(100)],
        "avg_review_score": [4.5 if i % 2 == 0 else 3.8 for i in range(100)],
        "customer_age_days": [30 + i * 2 for i in range(100)],
        "avg_order_value": [100.0 + i * 5.0 for i in range(100)],
    }
    return pd.DataFrame(data)


def test_empty_query_handling(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("")
    assert ans.intent == "empty_query"
    assert "Please enter a question" in ans.detailed_answer


def test_high_value_high_risk_query(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("Which customers are high-value and high-risk?")
    assert ans.intent == "high_value_high_risk"
    assert "at_risk_vip_count" in ans.metrics
    assert len(ans.evidence_points) >= 2
    assert ans.recommended_action is not None
    assert "confidence_rating" in ans.__dict__ or hasattr(ans, "confidence_rating")


def test_segment_revenue_leader_query(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("Which segment generates the most revenue?")
    assert ans.intent == "segment_revenue_leader"
    assert "leading_segment" in ans.metrics
    assert ans.metrics["segment_revenue_brl"] > 0
    assert len(ans.evidence_points) >= 1


def test_repeat_rate_query(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("What is our repeat purchase rate?")
    assert ans.intent == "repeat_rate_opportunity"
    assert "repeat_rate_pct" in ans.metrics
    assert ans.metrics["repeat_customers"] == 15


def test_macro_overview_query(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("Give me a macro summary of customer KPIs")
    assert ans.intent == "macro_overview"
    assert ans.metrics["total_customers"] == 100
    assert ans.metrics["total_gmv_brl"] > 0


def test_geographic_hubs_query(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("Which geographic regions have the top spend?")
    assert ans.intent == "geographic_hubs"
    assert "leading_state" in ans.metrics
    assert ans.metrics["state_revenue_brl"] > 0


def test_clv_benchmark_query(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("What is the average 12-month forward CLV?")
    assert ans.intent == "clv_benchmark"
    assert "average_12m_clv_brl" in ans.metrics
    assert "p90_threshold_brl" in ans.metrics


def test_explain_customer_risk_query_with_context(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("Explain risk for this customer", context_customer_id="cust_0050")
    assert ans.intent == "customer_risk_explanation"
    assert ans.metrics.get("customer_id") == "cust_0050"
    assert "health_score" in ans.metrics


def test_fallback_unsupported_query(sample_customer_df):
    service = GroundedAIService(sample_customer_df)
    ans = service.ask("What is the weather in London?")
    assert ans.intent == "unsupported_or_ambiguous"
    assert "Supported inquiries include" in ans.evidence_points[0]
