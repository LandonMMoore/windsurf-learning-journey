from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class AwardBase(BaseModel):
    sponsor: Optional[str] = None
    award_name: Optional[str] = None


class AwardCreate(AwardBase):
    pass


class AwardUpdate(AwardBase):
    pass


class AwardFind(make_optional(FindBase), make_optional(AwardBase)):
    pass


class AwardInfo(ModelBaseInfo, AwardBase):
    pass


class AwardListResponse(FindResult):
    founds: Optional[List[AwardInfo]] = None
    search_options: Optional[SearchOptions] = None
