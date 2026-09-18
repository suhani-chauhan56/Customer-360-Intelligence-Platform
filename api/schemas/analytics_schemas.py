"""Analytics and Insights Pydantic schemas for CustomerAtlas API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PortfolioOverviewSchema(BaseModel):
    """Macro executive portfolio health overview schema."""
    total_customers: int
    active_customers: int
    active_rate: float
    total_gmv: float
    avg_customer_value: float
    avg_order_value: float
    repeat_customer_rate: float
    at_risk_customers_count: int
    at_risk_revenue_exposure: float
    high_value_customers_count: int


class StructuredInsightSchema(BaseModel):
    """Evidence-backed structured business insight schema."""
    title: str
    observation: str
    evidence: str
    implication: str
    badge: str
    kind: str


class RecommendationItemSchema(BaseModel):
    """Single Next-Best-Category offer schema."""
    rank: int
    recommended_category: str
    reason: str
    method: str


class AskAtlasRequestSchema(BaseModel):
    """Request schema for grounded natural language analytics inquiries."""
    query: str
    context_customer_id: Optional[str] = None


class AskAtlasResponseSchema(BaseModel):
    """Evidence-grounded response schema for natural language inquiries."""
    query: str
    intent: str
    headline: str
    detailed_answer: str
    metrics: Dict[str, Any]
    evidence_points: List[str]
    recommended_action: Optional[str] = None
    data_source: str
    confidence_rating: str
    limitations_disclaimer: str
