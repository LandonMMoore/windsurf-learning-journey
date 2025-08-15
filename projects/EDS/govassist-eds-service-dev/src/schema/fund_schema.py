from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class FundBase(BaseModel):
    fund_number: Optional[int] = None
    fund_name: Optional[str] = None


class FundCreate(FundBase):
    pass


class FundUpdate(FundBase):
    pass


class FundFind(make_optional(FindBase), make_optional(FundBase)):
    pass


class FundInfo(ModelBaseInfo, FundBase):
    pass


class FundListResponse(FindResult):
    founds: Optional[List[FundInfo]] = None
    search_options: Optional[SearchOptions] = None
