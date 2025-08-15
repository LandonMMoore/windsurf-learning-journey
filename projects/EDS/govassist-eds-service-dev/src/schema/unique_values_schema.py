from typing import List, Optional

from pydantic import BaseModel, Field


class UniqueValuesRequest(BaseModel):
    """Request model for unique values endpoint."""

    index: str = Field(..., description="Elasticsearch index name")
    field: str = Field(..., description="Field name to extract unique values for")
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=10, ge=1, le=1000, description="Number of items per page")
    search: Optional[str] = Field(
        default=None, description="Search term to filter values"
    )
    order: str = Field(
        default="asc", pattern="^(asc|desc)$", description="Sort order: asc or desc"
    )


class UniqueValuesResponse(BaseModel):
    """Response model for unique values endpoint."""

    values: List[str] = Field(..., description="List of unique values")
    total: int = Field(..., description="Total number of unique values found")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
