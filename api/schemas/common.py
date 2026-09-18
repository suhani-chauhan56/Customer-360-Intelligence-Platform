"""Common Pydantic request/response schemas for CustomerAtlas REST API."""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized enterprise API envelope response."""
    success: bool = Field(default=True, description="Indicates whether the request completed successfully")
    data: Optional[T] = Field(default=None, description="Payload data returned by endpoint")
    message: Optional[str] = Field(default=None, description="Informational or success message")
    timestamp: Optional[str] = Field(default=None, description="Server timestamp of response generation")


class PaginationMeta(BaseModel):
    """Pagination metadata model."""
    total_records: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list response envelope."""
    success: bool = True
    items: List[T]
    pagination: PaginationMeta
