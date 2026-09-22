"""Machine learning model service helpers under src."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from analytics import MODELS_DIR


def load_model_artifact(model_name: str) -> Optional[Any]:
    """Safely load serialized joblib model."""
    path = MODELS_DIR / model_name
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception:
        return None


def predict_churn(
    model: Any,
    recency: float,
    frequency: float,
    monetary: float,
    aov: float,
    products: float,
    age: float,
) -> Tuple[float, str]:
    """Run churn probability inference and classify risk."""
    if model is None:
        return 0.5, "Unknown"

    cols = ["recency_days", "frequency", "monetary", "avg_order_value", "number_of_products", "customer_age_days"]
    in_df = pd.DataFrame([[recency, frequency, monetary, aov, products, age]], columns=cols)

    try:
        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(in_df)[0, 1])
        else:
            prob = float(model.predict(in_df)[0])
        prob = float(np.clip(prob, 0.0, 1.0))
    except Exception:
        prob = 0.5

    tier = "High Risk" if prob >= 0.65 else "Medium Risk" if prob >= 0.35 else "Low Risk"
    return prob, tier
