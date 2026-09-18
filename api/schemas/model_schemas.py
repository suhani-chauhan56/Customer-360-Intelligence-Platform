"""Machine Learning model inference and MLOps Pydantic schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModelInferenceInput(BaseModel):
    """Features required for real-time model inference."""
    recency_days: float = Field(..., ge=0, description="Days since last order")
    frequency: float = Field(..., ge=1, description="Lifetime completed orders")
    monetary: float = Field(..., ge=0, description="Total spend in BRL")
    avg_order_value: float = Field(..., ge=0, description="Average order value in BRL")
    number_of_products: float = Field(default=1, ge=1, description="Distinct products purchased")
    customer_age_days: float = Field(default=30, ge=1, description="Tenure span in days")


class ChurnPredictionResponse(BaseModel):
    """Churn model prediction output schema."""
    churn_probability: float
    risk_classification: str
    badge_color: str
    recommended_action: str


class CLVPredictionResponse(BaseModel):
    """12-Month CLV model prediction output schema."""
    predicted_12m_clv: float
    interval_low_80pct: float
    interval_high_80pct: float
    value_tier: str


class ModelRegistryItemSchema(BaseModel):
    """Model registry entry schema."""
    model_name: str
    artifact: str
    version: str
    algorithm: str
    status: str
    file_size_kb: float
