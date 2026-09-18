"""Segment and Audience Pydantic schemas for CustomerAtlas API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SegmentMetricSchema(BaseModel):
    """Segment aggregate performance schema."""
    rfm_segment: str
    customers: int
    customer_share: float
    total_revenue: float
    revenue_share: float
    avg_spend: float
    avg_clv: float
    avg_orders: float
    avg_recency: float
    avg_churn_prob: float


class SegmentComparisonSchema(BaseModel):
    """Side-by-side segment comparison schema."""
    metric: str
    segment_a: str
    segment_b: str
    val_a: str
    val_b: str
