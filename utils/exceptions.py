"""CustomerAtlas Custom Exceptions."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "streamlit_app"
for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from streamlit_app.utils.exceptions import (
    CustomerAtlasError,
    DataValidationError,
    ModelError,
    ModelLoadError,
    ModelInferenceError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    TenantIsolationError,
)

__all__ = [
    "CustomerAtlasError",
    "DataValidationError",
    "ModelError",
    "ModelLoadError",
    "ModelInferenceError",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "TenantIsolationError",
]
