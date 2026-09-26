"""Compatibility re-export of canonical exception classes from utils.exceptions."""

from utils.exceptions import (
    CustomerAtlasError,
    DataValidationError,
    DataLoadError,
    ModelError,
    ModelLoadError,
    ModelInferenceError,
    ConfigurationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    TenantIsolationError,
)

__all__ = [
    "CustomerAtlasError",
    "DataValidationError",
    "DataLoadError",
    "ModelError",
    "ModelLoadError",
    "ModelInferenceError",
    "ConfigurationError",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "TenantIsolationError",
]
