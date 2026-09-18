"""Tests for ML model loading, inference verification, and metadata registry."""

import pandas as pd
import pytest
from services.model_service import (
    audit_model_registry,
    create_model_input_frame,
    get_model_metadata,
    load_ml_model,
    predict_churn_propensity,
    predict_forward_clv,
    TABULAR_MODEL_FEATURES,
)


def test_create_model_input_frame():
    input_df = create_model_input_frame(
        recency=30,
        frequency=2,
        monetary=250.0,
        avg_order_value=125.0,
        products=2,
        age=60,
    )
    assert len(input_df) == 1
    assert list(input_df.columns) == TABULAR_MODEL_FEATURES


def test_get_model_metadata():
    meta = get_model_metadata("churn_model_metadata.json")
    assert meta.get("model_name") is not None
    assert meta.get("version") == "1.0.0"
    assert "features" in meta


def test_audit_model_registry():
    registry = audit_model_registry()
    assert len(registry) == 4
    names = [m["Model Name"] for m in registry]
    assert any("Churn" in n for n in names)
    assert any("CLV" in n for n in names)


def test_real_model_inference_churn():
    model = load_ml_model("churn_model.pkl")
    if model is not None:
        input_df = create_model_input_frame(60, 2, 300, 150, 2, 45)
        prob, band, color = predict_churn_propensity(model, input_df)
        assert 0.0 <= prob <= 1.0
        assert band in {"Low Risk", "Medium Risk", "High Risk"}


def test_real_model_inference_clv():
    model = load_ml_model("clv_model.pkl")
    if model is not None:
        input_df = create_model_input_frame(60, 2, 300, 150, 2, 45)
        clv, low, high = predict_forward_clv(model, input_df)
        assert clv >= 0.0
        assert low <= clv <= high
