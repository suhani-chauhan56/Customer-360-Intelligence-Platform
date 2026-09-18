"""Custom domain and infrastructure exceptions for CustomerAtlas.

Provides granular error types to differentiate data issues, model loading
failures, inference errors, and configuration issues.
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


class ModelLoadError(CustomerAtlasError):
    """Raised when an ML model artifact cannot be located or deserialized."""
    pass


class ModelInferenceError(CustomerAtlasError):
    """Raised when feature inputs fail schema compatibility during inference."""
    pass


class ConfigurationError(CustomerAtlasError):
    """Raised when environment or configuration parameters are invalid."""
    pass
