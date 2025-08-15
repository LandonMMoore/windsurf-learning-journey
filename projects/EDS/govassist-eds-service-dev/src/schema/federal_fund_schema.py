from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class FederalFundBase(BaseModel):
    fund_code: str
    fund_available: float
    fund_obligations: float
    fund_unobligated_balance: float
    fund_pending_obligations: float
    fund_pending_unobligated_balance: float
    fund_advance_construction: float


class FederalFundCreate(FederalFundBase):
    pass


class FederalFundUpdate(FederalFundBase):
    pass


class FederalFundFind(make_optional(FindBase), make_optional(FederalFundBase)):
    pass


class FederalFundInfo(ModelBaseInfo, FederalFundBase):
    pass


class FederalFundListResponse(FindResult):
    founds: Optional[List[FederalFundInfo]] = None
    search_options: Optional[SearchOptions] = None
