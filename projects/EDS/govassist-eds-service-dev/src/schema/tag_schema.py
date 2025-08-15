from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagFind(make_optional(FindBase), make_optional(TagBase)):
    pass


class TagInfo(ModelBaseInfo, TagBase):
    pass


class TagListResponse(FindResult):
    founds: Optional[List[TagInfo]] = None
    search_options: Optional[SearchOptions] = None
