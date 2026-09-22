"""Customer Intelligence API endpoints for CustomerAtlas."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user, require_permission, get_db_session
from api.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from api.schemas.customer_schemas import (
    Customer360Schema,
    CustomerHealthVitalSchema,
    CustomerSimulationRequest,
    CustomerSummarySchema,
)
from database.repositories.customer_repository import CustomerRepository
from security.auth import UserContext
from security.rbac import Permission
from services.customer_service import (
    compute_customer_health,
    derive_lifecycle_stages,
    diagnose_customer_risk_factors,
    explain_rfm_segment,
    get_customer_profile,
    search_customers,
)
from services.data_service import load_csv, retention_action
from services.health_score_service import calculate_customer_health_score, classify_lifecycle_state
from services.simulation_service import simulate_customer_value_shift
from services.audit_service import record_audit_event

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=PaginatedResponse[CustomerSummarySchema])
def list_customers(
    search: Optional[str] = Query(None, description="Search by Customer ID or City"),
    segment: Optional[str] = Query(None, description="Filter by RFM Segment"),
    risk_level: Optional[str] = Query(None, description="Filter by Risk Level"),
    state: Optional[str] = Query(None, description="Filter by State code"),
    clv_band: Optional[str] = Query(None, description="Filter by CLV Band"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("total_spend", description="Sort field"),
    sort_desc: bool = Query(True, description="Sort descending"),
    current_user: UserContext = Depends(require_permission(Permission.SEARCH_CUSTOMERS)),
    db: Session = Depends(get_db_session),
):
    """Retrieve filtered, paginated list of canonical customer profiles."""
    df = load_csv("customer_360_features.csv")
    if df.empty:
        raise HTTPException(status_code=503, detail="Customer feature store is temporarily unavailable.")

    filtered_df = search_customers(
        df=df,
        search_query=search or "",
        segment=segment or "All",
        risk_level=risk_level or "All",
        state=state or "All",
        clv_band=clv_band or "All",
    )

    if sort_by and sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=not sort_desc)

    total_records = len(filtered_df)
    total_pages = max(1, (total_records + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_records)

    page_records = filtered_df.iloc[start_idx:end_idx]

    items = [
        CustomerSummarySchema(
            customer_id=str(r["customer_id"]),
            rfm_segment=str(r.get("rfm_segment", "Regular Customers")),
            city=str(r.get("city", "Unknown")),
            state=str(r.get("state", "SP")),
            total_spend=float(r.get("total_spend", 0.0)),
            total_orders=int(r.get("total_orders", 1)),
            avg_order_value=float(r.get("avg_order_value", 0.0)),
            recency_days=int(r.get("recency_days", 0)),
            predicted_clv=float(r.get("predicted_clv", 0.0)),
            churn_probability=float(r.get("churn_probability", 0.0)),
            churn_risk_band=str(r.get("churn_risk_band", "Low")),
            clv_band=str(r.get("clv_band", "Bronze")),
        )
        for _, r in page_records.iterrows()
    ]

    return PaginatedResponse(
        success=True,
        items=items,
        pagination=PaginationMeta(
            total_records=total_records,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get("/{customer_id}/360", response_model=APIResponse[Customer360Schema])
def get_customer_360(
    customer_id: str,
    current_user: UserContext = Depends(require_permission(Permission.VIEW_CUSTOMER_360)),
):
    """Retrieve complete 360-degree profile for an individual customer."""
    df = load_csv("customer_360_features.csv")
    profile = get_customer_profile(df, customer_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Customer ID '{customer_id}' not found.")

    health_vitals = compute_customer_health(profile)
    lifecycle_stages = derive_lifecycle_stages(profile)
    risk_diag = diagnose_customer_risk_factors(profile)
    rfm_diag = explain_rfm_segment(profile)
    health_score_info = calculate_customer_health_score(profile)
    lifecycle_info = classify_lifecycle_state(profile)
    action_info = retention_action(float(profile.get("churn_probability", 0.0)), str(profile.get("rfm_segment", "")))

    # Record audit log event
    record_audit_event(
        action="CUSTOMER_360_VIEWED",
        resource_type="Customer",
        resource_id=customer_id,
        user_id=current_user.user_id,
        org_id=current_user.org_id,
    )

    data = Customer360Schema(
        customer_id=str(profile.get("customer_id")),
        rfm_segment=str(profile.get("rfm_segment", "Regular Customers")),
        cluster_segment=str(profile.get("cluster_segment", "Standard")),
        city=str(profile.get("city", "Unknown")).title(),
        state=str(profile.get("state", "SP")).upper(),
        favorite_category=str(profile.get("favorite_category", "General")),
        first_purchase_date=str(profile.get("first_purchase_date"))[:10] if profile.get("first_purchase_date") else None,
        last_purchase_date=str(profile.get("last_purchase_date"))[:10] if profile.get("last_purchase_date") else None,
        total_spend=float(profile.get("total_spend", 0.0)),
        total_orders=int(profile.get("total_orders", 1)),
        avg_order_value=float(profile.get("avg_order_value", 0.0)),
        recency_days=int(profile.get("recency_days", 0)),
        predicted_clv=float(profile.get("predicted_clv", 0.0)),
        predicted_90d_revenue=float(profile.get("predicted_90d_revenue", 0.0)),
        clv_band=str(profile.get("clv_band", "Bronze")),
        churn_probability=float(profile.get("churn_probability", 0.0)),
        churn_risk_band=str(profile.get("churn_risk_band", "Low")),
        health_score=health_score_info["score"],
        health_tier=health_score_info["health_tier"],
        lifecycle_state=lifecycle_info["lifecycle_state"],
        retention_playbook=action_info,
        health_vitals=[CustomerHealthVitalSchema(**v) for v in health_vitals],
        lifecycle_stages=lifecycle_stages,
        risk_diagnostics=risk_diag,
        rfm_explanation=rfm_diag,
    )

    return APIResponse(success=True, data=data)


@router.post("/{customer_id}/simulate", response_model=APIResponse[dict])
def simulate_customer_scenario(
    customer_id: str,
    payload: CustomerSimulationRequest,
    current_user: UserContext = Depends(require_permission(Permission.RUN_SIMULATION)),
):
    """Run What-If analytical simulation for a customer profile."""
    df = load_csv("customer_360_features.csv")
    profile = get_customer_profile(df, customer_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Customer ID '{customer_id}' not found.")

    simulation_result = simulate_customer_value_shift(
        profile=profile,
        additional_orders=payload.additional_orders,
        aov_multiplier=payload.aov_multiplier,
        recency_reduction_days=payload.recency_reduction_days,
    )

    record_audit_event(
        action="SIMULATION_EXECUTED",
        resource_type="Customer",
        resource_id=customer_id,
        user_id=current_user.user_id,
        org_id=current_user.org_id,
        details=f"orders={payload.additional_orders}, aov_mult={payload.aov_multiplier}",
    )

    return APIResponse(success=True, data=simulation_result)
