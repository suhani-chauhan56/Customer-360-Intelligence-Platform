"""Customer Pydantic request and response schemas for CustomerAtlas API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CustomerSummarySchema(BaseModel):
    """Brief customer profile schema for lists and explorer tables."""
    customer_id: str
    rfm_segment: str
    city: Optional[str] = None
    state: Optional[str] = None
    total_spend: float
    total_orders: int
    avg_order_value: float
    recency_days: int
    predicted_clv: float
    churn_probability: float
    churn_risk_band: str
    clv_band: str


class CustomerHealthVitalSchema(BaseModel):
    """Single health dimension score."""
    dimension: str
    rating: str
    detail: str
    color: str
    icon: str


class Customer360Schema(BaseModel):
    """Complete Customer 360 profile response schema."""
    customer_id: str
    rfm_segment: str
    cluster_segment: str
    city: str
    state: str
    favorite_category: str
    first_purchase_date: Optional[str] = None
    last_purchase_date: Optional[str] = None
    
    # Financials & Value
    total_spend: float
    total_orders: int
    avg_order_value: float
    recency_days: int
    predicted_clv: float
    predicted_90d_revenue: float
    clv_band: str

    # Health & Risk
    churn_probability: float
    churn_risk_band: str
    health_score: float
    health_tier: str
    lifecycle_state: str
    retention_playbook: Dict[str, str]

    # Vitals & Insights
    health_vitals: List[CustomerHealthVitalSchema]
    lifecycle_stages: List[Dict[str, Any]]
    risk_diagnostics: Dict[str, Any]
    rfm_explanation: Dict[str, Any]


class CustomerSimulationRequest(BaseModel):
    """Request payload for What-If scenario simulation."""
    additional_orders: int = Field(default=1, ge=1, le=50, description="Hypothetical additional orders placed")
    aov_multiplier: float = Field(default=1.0, ge=0.1, le=10.0, description="Average order value shift multiplier")
    recency_reduction_days: int = Field(default=30, ge=0, le=365, description="Days by which inactivity is reduced")
