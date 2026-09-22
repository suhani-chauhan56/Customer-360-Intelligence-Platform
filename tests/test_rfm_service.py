"""Unit tests for RFM Intelligence Service in CustomerAtlas."""

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
    assert overview["avg_frequency"] > 0
    assert overview["avg_monetary"] > 0


def test_compute_rfm_overview_empty(empty_customer_df: pd.DataFrame):
    overview = compute_rfm_overview(empty_customer_df)
    assert overview["total_customers"] == 0
    assert overview["avg_recency"] == 0.0


def test_compute_segment_distribution(sample_customer_df: pd.DataFrame):
    dist = compute_segment_distribution(sample_customer_df)
    assert not dist.empty
    assert "rfm_segment" in dist.columns
    assert "customer_share" in dist.columns
    assert "revenue_share" in dist.columns
    assert round(dist["customer_share"].sum(), 2) == 1.0


def test_compare_segments(sample_customer_df: pd.DataFrame):
    comp = compare_segments(sample_customer_df, "Champions", "Lost Customers")
    assert len(comp) > 0
    metrics = [c["metric"] for c in comp]
    assert "Customer Count" in metrics
    assert "Total Revenue (GMV)" in metrics


def test_get_segment_playbook():
    playbook_champ = get_segment_playbook("Champions")
    assert "Champions" in playbook_champ["title"]
    assert len(playbook_champ["actions"]) >= 1

    playbook_unknown = get_segment_playbook("Unknown Segment")
    assert "Strategy" in playbook_unknown["title"]
