"""Unit tests for Grounded AI Assistant Service in CustomerAtlas."""

import pandas as pd
import pytest
from services.grounded_ai_service import GroundedAIService, GroundedAnswer


def test_ask_empty_query(sample_customer_df: pd.DataFrame):
    ai = GroundedAIService(sample_customer_df)
    ans = ai.ask("")
    assert ans.intent == "empty_query"
    assert "No Question" in ans.headline


def test_ask_high_value_high_risk(sample_customer_df: pd.DataFrame):
    ai = GroundedAIService(sample_customer_df)
    ans = ai.ask("Which customers are high value and high risk?")
    assert ans.intent == "high_value_high_risk"
    assert ans.headline != ""
    assert "revenue_exposed_brl" in ans.metrics


def test_ask_segment_leader(sample_customer_df: pd.DataFrame):
    ai = GroundedAIService(sample_customer_df)
    ans = ai.ask("Which segment generates the most revenue?")
    assert ans.intent == "segment_revenue_leader"
    assert "leading_segment" in ans.metrics


def test_ask_macro_overview(sample_customer_df: pd.DataFrame):
    ai = GroundedAIService(sample_customer_df)
    ans = ai.ask("What is our total revenue overview?")
    assert ans.intent == "macro_overview"
    assert "total_gmv_brl" in ans.metrics


def test_ask_customer_risk_explanation(sample_customer_df: pd.DataFrame):
    ai = GroundedAIService(sample_customer_df)
    ans = ai.ask("Explain risk for this customer", context_customer_id="cust_001")
    assert ans.intent == "customer_risk_explanation"
    assert ans.metrics.get("customer_id") == "cust_001"
    assert len(ans.evidence_points) > 0


def test_ask_unsupported(sample_customer_df: pd.DataFrame):
    ai = GroundedAIService(sample_customer_df)
    ans = ai.ask("Tell me a fictional story about space aliens")
    assert ans.intent == "unsupported_or_ambiguous"
    assert ans.recommended_action is not None
