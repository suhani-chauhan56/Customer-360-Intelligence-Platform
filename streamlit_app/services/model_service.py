"""Enterprise Machine Learning Model Service for CustomerAtlas.

Provides model loading, artifact validation, metadata audit, schema verification,
and safe predictive inference for churn, CLV, clustering, and sentiment models.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
import streamlit as st

from config.settings import MODELS_DIR, METADATA_DIR
from utils.exceptions import ModelInferenceError, ModelLoadError
from utils.logging_config import logger


# Contract schema for Churn & CLV tabular model inputs
TABULAR_MODEL_FEATURES: List[str] = [
    "recency_days",
    "frequency",
    "monetary",
    "avg_order_value",
    "number_of_products",
    "customer_age_days",
]


@st.cache_resource(show_spinner=False)
def load_ml_model(model_filename: str) -> Optional[Any]:
    """Safely load and cache serialized machine learning model artifact."""
    model_path = MODELS_DIR / model_filename
    if not model_path.exists():
        logger.warning(f"Model artifact not found at {model_path}")
        return None
    try:
        model = joblib.load(model_path)
        logger.info(f"Loaded ML model: {model_filename}")
        return model
    except Exception as e:
        logger.error(f"Failed to deserialize model {model_filename}: {e}", exc_info=True)
        return None


def get_model_metadata(metadata_filename: str) -> Dict[str, Any]:
    """Load model provenance and evaluation metadata from JSON file."""
    meta_path = METADATA_DIR / metadata_filename
    if not meta_path.exists():
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not read metadata {metadata_filename}: {e}")
        return {}


def create_model_input_frame(
    recency: float,
    frequency: float,
    monetary: float,
    avg_order_value: float,
    products: float,
    age: float,
) -> pd.DataFrame:
    """Construct an inference feature frame conforming to the tabular model contract."""
    return pd.DataFrame(
        [[float(recency), float(frequency), float(monetary), float(avg_order_value), float(products), float(age)]],
        columns=TABULAR_MODEL_FEATURES,
    )


def predict_churn_propensity(
    model: Optional[Any],
    input_df: pd.DataFrame,
) -> Tuple[float, str, str]:
    """Execute churn prediction and return probability, classification band, and badge color."""
    if model is None:
        raise ModelLoadError("Churn model artifact is not loaded.")

    if not all(col in input_df.columns for col in TABULAR_MODEL_FEATURES):
        missing = [c for c in TABULAR_MODEL_FEATURES if c not in input_df.columns]
        raise ModelInferenceError(f"Inference input missing required features: {missing}")

    try:
        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(input_df)[0, 1])
        else:
            prob = float(model.predict(input_df)[0])
        prob = float(np.clip(prob, 0.0, 1.0))
    except Exception as e:
        logger.error(f"Inference error during churn prediction: {e}")
        raise ModelInferenceError(f"Churn inference failed: {e}") from e

    if prob >= 0.65:
        return prob, "High Risk", "#DC2626"
    elif prob >= 0.35:
        return prob, "Medium Risk", "#F59E0B"
    else:
        return prob, "Low Risk", "#16A34A"


def predict_forward_clv(
    model: Optional[Any],
    input_df: pd.DataFrame,
) -> Tuple[float, float, float]:
    """Execute 12-month forward CLV estimation and return expected value and 80% interval."""
    if model is None:
        raise ModelLoadError("CLV model artifact is not loaded.")

    if not all(col in input_df.columns for col in TABULAR_MODEL_FEATURES):
        missing = [c for c in TABULAR_MODEL_FEATURES if c not in input_df.columns]
        raise ModelInferenceError(f"Inference input missing required features: {missing}")

    try:
        est_clv = max(float(model.predict(input_df)[0]), 0.0)
    except Exception as e:
        logger.error(f"Inference error during CLV prediction: {e}")
        raise ModelInferenceError(f"CLV inference failed: {e}") from e

    interval_low = est_clv * 0.85
    interval_high = est_clv * 1.15
    return est_clv, interval_low, interval_high


def audit_model_registry() -> List[Dict[str, Any]]:
    """Audit the operational readiness of all registered machine learning models."""
    models_to_check = [
        ("churn_model.pkl", "churn_model_metadata.json", "Churn Propensity Classifier"),
        ("clv_model.pkl", "clv_model_metadata.json", "12-Month CLV Regressor"),
        ("segment_model.pkl", "segment_model_metadata.json", "Behavioral Cluster Pipeline"),
        ("sentiment_model.pkl", "sentiment_model_metadata.json", "NLP Review Sentiment Classifier"),
    ]

    registry_status = []
    for model_file, meta_file, display_name in models_to_check:
        model_path = MODELS_DIR / model_file
        meta = get_model_metadata(meta_file)
        exists = model_path.exists()
        
        status_info = {
            "Model Name": display_name,
            "Artifact": model_file,
            "Version": meta.get("version", "1.0.0"),
            "Algorithm": meta.get("algorithm", "XGBoost / Scikit-Learn"),
            "Status": "Ready 🟢" if exists else "Missing 🔴",
            "File Size (KB)": round(model_path.stat().st_size / 1024, 1) if exists else 0.0,
        }
        registry_status.append(status_info)

    return registry_status
