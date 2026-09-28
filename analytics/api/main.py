"""FastAPI REST Service for CustomerAtlas AI Python Analytics & ML Pipeline.

Preserves the complete Python/Pandas/Scikit-learn/XGBoost data science ecosystem.
"""

from pathlib import Path
import os
import sys
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Resolve project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from analytics import (
    load_dataset,
    validate_dataset,
    compute_executive_kpis,
    compute_rfm_distribution,
    compute_clv_brackets,
    prioritize_retention_queue,
    calculate_health_score,
    classify_lifecycle_stage,
    calculate_population_stability_index,
)
from streamlit_app.services.customer_service import diagnose_customer_risk_factors, explain_rfm_segment
from streamlit_app.services.grounded_ai_service import GroundedAIService
from streamlit_app.services.model_service import (
    load_ml_model,
    create_model_input_frame,
    predict_churn_propensity,
    predict_forward_clv,
    audit_model_registry,
)

app = FastAPI(
    title="CustomerAtlas AI Python Analytics & ML Service",
    version="2.0.0",
    description="Production REST API providing ML inference, RFM calculations, and grounded AI decision support.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dataset cache
_df_cache: Optional[Any] = None
_churn_model: Optional[Any] = None
_clv_model: Optional[Any] = None
_ai_service: Optional[GroundedAIService] = None


def get_data():
    global _df_cache, _ai_service
    if _df_cache is None or _df_cache.empty:
        _df_cache = load_dataset("customer_360_features.csv")
        _ai_service = GroundedAIService(_df_cache)
    return _df_cache


@app.on_event("startup")
def startup_event():
    global _churn_model, _clv_model
    try:
        get_data()
        _churn_model = load_ml_model("churn_model.pkl")
        _clv_model = load_ml_model("clv_model.pkl")
    except Exception as e:
        print(f"Startup loading note: {e}")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CustomerAtlas Python Analytics & ML Microservice",
        "dataset_loaded": _df_cache is not None and not _df_cache.empty,
        "records_count": len(_df_cache) if _df_cache is not None else 0,
    }


@app.get("/api/v1/overview")
def get_overview_kpis():
    df = get_data()
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Customer dataset is unavailable.")
    kpis = compute_executive_kpis(df)
    return {"status": "success", "data": kpis.__dict__}


@app.get("/api/v1/rfm")
def get_rfm_segments():
    df = get_data()
    segments_df = compute_rfm_distribution(df)
    return {"status": "success", "data": segments_df.to_dict(orient="records")}


@app.get("/api/v1/clv")
def get_clv_analytics():
    df = get_data()
    clv_bins = compute_clv_brackets(df)
    return {"status": "success", "data": clv_bins.to_dict(orient="records")}


@app.get("/api/v1/churn/retention-queue")
def get_retention_queue(top_n: int = Query(default=50, ge=1, le=500)):
    df = get_data()
    queue = prioritize_retention_queue(df, top_n=top_n)
    return {"status": "success", "data": queue.to_dict(orient="records")}


class ModelInferenceInput(BaseModel):
    recency_days: float = Field(default=90.0)
    frequency: float = Field(default=1.0)
    monetary: float = Field(default=150.0)
    avg_order_value: float = Field(default=150.0)
    number_of_products: float = Field(default=1.0)
    customer_age_days: float = Field(default=180.0)


@app.post("/api/v1/predict/churn")
def predict_churn(input_data: ModelInferenceInput):
    global _churn_model
    if _churn_model is None:
        _churn_model = load_ml_model("churn_model.pkl")

    frame = create_model_input_frame(
        input_data.recency_days,
        input_data.frequency,
        input_data.monetary,
        input_data.avg_order_value,
        input_data.number_of_products,
        input_data.customer_age_days,
    )
    prob, tier, color = predict_churn_propensity(_churn_model, frame)
    return {
        "status": "success",
        "data": {
            "churn_probability": prob,
            "risk_tier": tier,
            "badge_color": color,
        },
    }


@app.post("/api/v1/predict/clv")
def predict_clv(input_data: ModelInferenceInput):
    global _clv_model
    if _clv_model is None:
        _clv_model = load_ml_model("clv_model.pkl")

    frame = create_model_input_frame(
        input_data.recency_days,
        input_data.frequency,
        input_data.monetary,
        input_data.avg_order_value,
        input_data.number_of_products,
        input_data.customer_age_days,
    )
    est_clv, low_ci, high_ci = predict_forward_clv(_clv_model, frame)
    return {
        "status": "success",
        "data": {
            "predicted_clv": est_clv,
            "ci_low": low_ci,
            "ci_high": high_ci,
        },
    }


class GroundedAIRequest(BaseModel):
    query: str
    customer_id: Optional[str] = None


@app.post("/api/v1/ai/ask")
def ask_grounded_ai(req: GroundedAIRequest):
    global _ai_service
    get_data()
    if _ai_service is None:
        _ai_service = GroundedAIService(_df_cache)
    answer = _ai_service.ask(req.query, req.customer_id)
    return {"status": "success", "data": answer.__dict__}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
