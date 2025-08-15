from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class FhwaAwardTypeBase(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None


class FhwaAwardTypeCreate(FhwaAwardTypeBase):
    pass


class FhwaAwardTypeUpdate(FhwaAwardTypeBase):
    pass


class FhwaAwardTypeFind(make_optional(FindBase), make_optional(FhwaAwardTypeBase)):
    pass


class FhwaAwardTypeInfo(ModelBaseInfo, FhwaAwardTypeBase):
    pass


class FhwaAwardTypeListResponse(FindResult):
    founds: Optional[List[FhwaAwardTypeInfo]] = None
    search_options: Optional[SearchOptions] = None
