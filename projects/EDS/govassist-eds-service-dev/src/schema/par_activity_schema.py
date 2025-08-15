from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class ParActivityBase(BaseModel):
    par_id: Optional[int] = None
    activity: Optional[str] = None
    status: Optional[str] = None
    date: Optional[datetime] = None
    user: Optional[str] = None
    comments: Optional[str] = None


class ParActivityCreate(ParActivityBase):
    par_id: int


class ParActivityUpdate(ParActivityBase):
    pass


class ParActivityFind(make_optional(FindBase), make_optional(ParActivityBase)):
    pass


class ParActivityInfo(ModelBaseInfo, ParActivityBase):
    pass


class ParActivityListResponse(FindResult):
    founds: Optional[List[ParActivityInfo]] = None
    search_options: Optional[SearchOptions] = None
