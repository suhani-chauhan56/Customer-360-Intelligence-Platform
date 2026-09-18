"""Executive Analytics and Insights API endpoints for CustomerAtlas."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import require_permission
from api.schemas.analytics_schemas import (
    PortfolioOverviewSchema,
    RecommendationItemSchema,
    StructuredInsightSchema,
)
from api.schemas.common import APIResponse
from security.auth import UserContext
from security.rbac import Permission
from services.data_service import load_csv
from services.insight_service import generate_executive_insights
from services.recommendation_service import get_customer_recommendations

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=APIResponse[PortfolioOverviewSchema])
def get_portfolio_overview(
    current_user: UserContext = Depends(require_permission(Permission.VIEW_ANALYTICS)),
):
    """Retrieve macro executive portfolio health metrics."""
    df = load_csv("customer_360_features.csv")
    if df.empty:
        raise HTTPException(status_code=503, detail="Customer dataset unavailable.")

    total_customers = int(df["customer_id"].nunique())
    total_gmv = float(df["total_spend"].sum())
    total_orders = int(df["total_orders"].sum())
    avg_customer_value = total_gmv / max(1, total_customers)
    avg_order_value = total_gmv / max(1, total_orders)
    
    repeat_customers = int((df["total_orders"] > 1).sum())
    repeat_rate = repeat_customers / max(1, total_customers)
    active_customers = int((df["recency_days"] <= 180).sum())
    active_rate = active_customers / max(1, total_customers)
    
    at_risk_df = df[df["churn_probability"] >= 0.65]
    at_risk_count = len(at_risk_df)
    at_risk_rev = float(at_risk_df["total_spend"].sum())
    
    p90_clv = float(df["predicted_clv"].quantile(0.90))
    high_val_count = int((df["predicted_clv"] >= p90_clv).sum())

    data = PortfolioOverviewSchema(
        total_customers=total_customers,
        active_customers=active_customers,
        active_rate=round(active_rate, 4),
        total_gmv=round(total_gmv, 2),
        avg_customer_value=round(avg_customer_value, 2),
        avg_order_value=round(avg_order_value, 2),
        repeat_customer_rate=round(repeat_rate, 4),
        at_risk_customers_count=at_risk_count,
        at_risk_revenue_exposure=round(at_risk_rev, 2),
        high_value_customers_count=high_val_count,
    )
    return APIResponse(success=True, data=data)


@router.get("/insights", response_model=APIResponse[List[StructuredInsightSchema]])
def get_structured_insights(
    current_user: UserContext = Depends(require_permission(Permission.VIEW_ANALYTICS)),
):
    """Retrieve evidence-backed structured business insights."""
    df = load_csv("customer_360_features.csv")
    if df.empty:
        raise HTTPException(status_code=503, detail="Customer dataset unavailable.")

    raw_insights = generate_executive_insights(df)
    items = [StructuredInsightSchema(**i) for i in raw_insights]
    return APIResponse(success=True, data=items)


@router.get("/recommendations/{customer_id}", response_model=APIResponse[List[RecommendationItemSchema]])
def get_recommendations_for_customer(
    customer_id: str,
    current_user: UserContext = Depends(require_permission(Permission.VIEW_CUSTOMER_360)),
):
    """Retrieve ranked explainable Next-Best-Category recommendations for a customer."""
    recs_df = load_csv("recommendations.csv")
    recs = get_customer_recommendations(recs_df, customer_id, top_n=5)
    items = [RecommendationItemSchema(**r) for r in recs]
    return APIResponse(success=True, data=items)
