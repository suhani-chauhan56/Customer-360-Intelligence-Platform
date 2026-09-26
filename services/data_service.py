"""Root package proxy for data_service."""
from streamlit_app.services.data_service import (
    MODEL_COLUMNS,
    build_customer_pdf,
    load_csv,
    load_model,
    model_input_frame,
    retention_action,
)

__all__ = [
    "MODEL_COLUMNS",
    "build_customer_pdf",
    "load_csv",
    "load_model",
    "model_input_frame",
    "retention_action",
]
