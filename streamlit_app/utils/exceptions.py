"""Custom domain and infrastructure exceptions for CustomerAtlas.

Provides granular error types to differentiate data issues, model loading
failures, inference errors, authentication, and configuration issues.
Self-contained with zero external or circular dependencies.
"""


class CustomerAtlasError(Exception):
    """Base exception for all CustomerAtlas application errors."""
    pass


class DataValidationError(CustomerAtlasError):
    """Raised when dataset fails schema, type, or integrity validation."""
    pass


class DataLoadError(CustomerAtlasError):
    """Raised when an expected dataset file is missing or unreadable."""
    pass


class ModelError(CustomerAtlasError):
    """Base exception for ML model errors."""
    pass


class ModelLoadError(ModelError):
    """Raised when an ML model artifact cannot be located or deserialized."""
    pass


class ModelInferenceError(ModelError):
    """Raised when feature inputs fail schema compatibility during inference."""
    pass


class ConfigurationError(CustomerAtlasError):
    """Raised when environment or configuration parameters are invalid."""
    pass


class AuthenticationError(CustomerAtlasError):
    """Raised when authentication credentials are invalid or missing."""
    pass


class AuthorizationError(CustomerAtlasError):
    """Raised when user lacks required RBAC permissions."""
    pass


class ResourceNotFoundError(CustomerAtlasError):
    """Raised when a requested resource or customer is not found."""
    pass


class TenantIsolationError(CustomerAtlasError):
    """Raised when cross-tenant access violation occurs."""
    pass


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
