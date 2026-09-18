"""Machine Learning inference and MLOps API endpoints for CustomerAtlas."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import require_permission
from api.schemas.common import APIResponse
from api.schemas.model_schemas import (
    CLVPredictionResponse,
    ChurnPredictionResponse,
    ModelInferenceInput,
    ModelRegistryItemSchema,
)
from security.auth import UserContext
from security.rbac import Permission
from services.data_service import load_csv, retention_action
from services.drift_service import run_feature_drift_audit
from services.model_service import (
    audit_model_registry,
    create_model_input_frame,
    load_ml_model,
    predict_churn_propensity,
    predict_forward_clv,
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/models", response_model=APIResponse[List[ModelRegistryItemSchema]])
def list_model_registry(
    current_user: UserContext = Depends(require_permission(Permission.VIEW_ANALYTICS)),
):
    """Retrieve operational status and metadata for all registered models."""
    registry = audit_model_registry()
    items = [
        ModelRegistryItemSchema(
            model_name=r["Model Name"],
            artifact=r["Artifact"],
            version=r["Version"],
            algorithm=r["Algorithm"],
            status=r["Status"],
            file_size_kb=r["File Size (KB)"],
        )
        for r in registry
    ]
    return APIResponse(success=True, data=items)


@router.post("/predict/churn", response_model=APIResponse[ChurnPredictionResponse])
def predict_churn(
    payload: ModelInferenceInput,
    current_user: UserContext = Depends(require_permission(Permission.RUN_INFERENCE)),
):
    """Run real-time XGBoost inference for customer churn propensity."""
    model = load_ml_model("churn_model.pkl")
    if model is None:
        raise HTTPException(status_code=503, detail="Churn prediction model is not loaded.")

    input_df = create_model_input_frame(
        recency=payload.recency_days,
        frequency=payload.frequency,
        monetary=payload.monetary,
        avg_order_value=payload.avg_order_value,
        products=payload.number_of_products,
        age=payload.customer_age_days,
    )
    prob, band, color = predict_churn_propensity(model, input_df)
    action = retention_action(prob)["action"]

    return APIResponse(
        success=True,
        data=ChurnPredictionResponse(
            churn_probability=round(prob, 4),
            risk_classification=band,
            badge_color=color,
            recommended_action=action,
        ),
    )


@router.post("/predict/clv", response_model=APIResponse[CLVPredictionResponse])
def predict_clv(
    payload: ModelInferenceInput,
    current_user: UserContext = Depends(require_permission(Permission.RUN_INFERENCE)),
):
    """Run real-time XGBoost inference for 12-Month Forward Customer Lifetime Value."""
    model = load_ml_model("clv_model.pkl")
    if model is None:
        raise HTTPException(status_code=503, detail="CLV prediction model is not loaded.")

    input_df = create_model_input_frame(
        recency=payload.recency_days,
        frequency=payload.frequency,
        monetary=payload.monetary,
        avg_order_value=payload.avg_order_value,
        products=payload.number_of_products,
        age=payload.customer_age_days,
    )
    clv, low, high = predict_forward_clv(model, input_df)
    tier = "Platinum VIP" if clv >= 350.0 else "Gold Tier" if clv >= 180.0 else "Silver Tier" if clv >= 90.0 else "Bronze Tier"

    return APIResponse(
        success=True,
        data=CLVPredictionResponse(
            predicted_12m_clv=round(clv, 2),
            interval_low_80pct=round(low, 2),
            interval_high_80pct=round(high, 2),
            value_tier=tier,
        ),
    )


@router.get("/drift", response_model=APIResponse[dict])
def check_feature_drift(
    current_user: UserContext = Depends(require_permission(Permission.VIEW_DRIFT_MONITORING)),
):
    """Run Population Stability Index (PSI) drift monitoring across feature distributions."""
    df = load_csv("customer_360_features.csv")
    if df.empty:
        raise HTTPException(status_code=503, detail="Customer dataset unavailable for baseline.")

    # Split into historical baseline vs recent active subset to monitor distribution shift
    baseline_df = df[df["recency_days"] > 180]
    current_df = df[df["recency_days"] <= 180]

    report = run_feature_drift_audit(baseline_df, current_df)
    return APIResponse(success=True, data=report)
