"""Segment and Audience API endpoints for CustomerAtlas."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import require_permission
from api.schemas.common import APIResponse
from api.schemas.segment_schemas import SegmentComparisonSchema, SegmentMetricSchema
from security.auth import UserContext
from security.rbac import Permission
from services.data_service import load_csv
from services.rfm_service import compare_segments, compute_segment_distribution, get_segment_playbook

router = APIRouter(prefix="/segments", tags=["Segments"])


@router.get("", response_model=APIResponse[List[SegmentMetricSchema]])
def list_segments(
    current_user: UserContext = Depends(require_permission(Permission.VIEW_ANALYTICS)),
):
    """Retrieve RFM segment portfolio distribution and metrics."""
    df = load_csv("customer_360_features.csv")
    if df.empty:
        raise HTTPException(status_code=503, detail="Customer dataset unavailable.")

    summary_df = compute_segment_distribution(df)
    items = [
        SegmentMetricSchema(
            rfm_segment=str(r["rfm_segment"]),
            customers=int(r["customers"]),
            customer_share=round(float(r["customer_share"]), 4),
            total_revenue=round(float(r["total_revenue"]), 2),
            revenue_share=round(float(r["revenue_share"]), 4),
            avg_spend=round(float(r["avg_spend"]), 2),
            avg_clv=round(float(r["avg_clv"]), 2),
            avg_orders=round(float(r["avg_orders"]), 2),
            avg_recency=round(float(r["avg_recency"]), 1),
            avg_churn_prob=round(float(r["avg_churn_prob"]), 4),
        )
        for _, r in summary_df.iterrows()
    ]
    return APIResponse(success=True, data=items)


@router.get("/{segment_name}/playbook", response_model=APIResponse[dict])
def get_segment_strategy_playbook(
    segment_name: str,
    current_user: UserContext = Depends(require_permission(Permission.VIEW_ANALYTICS)),
):
    """Retrieve strategic action playbook for an RFM segment."""
    playbook = get_segment_playbook(segment_name)
    return APIResponse(success=True, data=playbook)


@router.get("/compare", response_model=APIResponse[List[SegmentComparisonSchema]])
def compare_two_segments(
    segment_a: str = Query(..., description="First segment name"),
    segment_b: str = Query(..., description="Second segment name"),
    current_user: UserContext = Depends(require_permission(Permission.COMPARE_CUSTOMERS)),
):
    """Compare two RFM segments side-by-side."""
    df = load_csv("customer_360_features.csv")
    if df.empty:
        raise HTTPException(status_code=503, detail="Customer dataset unavailable.")

    comp_results = compare_segments(df, segment_a, segment_b)
    items = [
        SegmentComparisonSchema(
            metric=str(c["metric"]),
            segment_a=segment_a,
            segment_b=segment_b,
            val_a=str(c["val_a"]),
            val_b=str(c["val_b"]),
        )
        for c in comp_results
    ]
    return APIResponse(success=True, data=items)
