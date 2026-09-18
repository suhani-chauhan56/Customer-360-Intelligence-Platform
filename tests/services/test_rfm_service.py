"""Tests for RFM intelligence and segmentation service."""

import pandas as pd
import pytest
from services.rfm_service import (
    compare_segments,
    compute_rfm_overview,
    compute_segment_distribution,
    get_segment_playbook,
)


def test_compute_rfm_overview(sample_customer_df: pd.DataFrame):
    overview = compute_rfm_overview(sample_customer_df)
    assert overview["total_customers"] == 3
    assert overview["avg_recency"] > 0
    assert overview["avg_frequency"] >= 1.0
    assert overview["avg_monetary"] > 0


def test_compute_segment_distribution(sample_customer_df: pd.DataFrame):
    seg_dist = compute_segment_distribution(sample_customer_df)
    assert not seg_dist.empty
    assert "customers" in seg_dist.columns
    assert "total_revenue" in seg_dist.columns
    assert "customer_share" in seg_dist.columns
    assert "revenue_share" in seg_dist.columns


def test_compare_segments(sample_customer_df: pd.DataFrame):
    comp = compare_segments(sample_customer_df, "Champions", "Lost Customers")
    assert len(comp) > 0
    metrics = [c["metric"] for c in comp]
    assert "Customer Count" in metrics
    assert "Total Revenue (GMV)" in metrics
    assert "Average 12M CLV" in metrics


def test_get_segment_playbook():
    pb_champ = get_segment_playbook("Champions")
    assert "VIP" in pb_champ["title"] or "Champions" in pb_champ["title"]
    assert len(pb_champ["actions"]) > 0

    pb_risk = get_segment_playbook("At Risk")
    assert "Win-Back" in pb_risk["title"] or "Risk" in pb_risk["title"]
