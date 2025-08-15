from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.util.schema import make_optional


class ModelBaseInfo(BaseModel):
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class FindBase(BaseModel):
    ordering: Optional[str] = None
    page: Optional[int] = 1
    page_size: Optional[int | str] = 10
    search: Optional[str] = None


class SearchOptions(FindBase):
    total_count: Optional[int] = None


class FindResult(BaseModel):
    founds: Optional[List] = None
    search_options: Optional[SearchOptions] = None


class FindDateRange(BaseModel):
    created_at__lt: Optional[str] = None
    created_at__lte: Optional[str] = None
    created_at__gt: Optional[str] = None
    created_at__gte: Optional[str] = None


class Blank(BaseModel):
    pass


class FindUniqueValues(make_optional(FindBase)):
    field_name: str


class UniqueValuesResult(BaseModel):
    founds: List[Any]
    search_options: Optional[SearchOptions] = None
