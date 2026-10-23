# app/core/schemas.py
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number", ge=1)
    size: int = Field(..., description="Number of items per page", ge=1)

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number starting from 1")
    size: int = Field(default=10, ge=1, le=100, description="Items per page (max 100)")