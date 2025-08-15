from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, constr, validator

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)
from src.schema.par_schema import ParData

ALPHANUMERIC_PATTERN = r"^[a-zA-Z0-9\s.,\-()&_/]+$"


class FundData(BaseModel):
    created_at: datetime
    updated_at: datetime
    fund_code: str
    ce: float
    construction: float
    difs_id: str
    id: str
    fund_type: str


class ParBudgetAnalysisResponse(BaseModel):
    par_data: ParData
    total_changes: dict
    justification: Optional[str] = None
    part_rate: Optional[float] = None
    # funds: List[FundData]


class ParBudgetAnalysisBase(BaseModel):
    par_id: Optional[int] = None
    project_details_id: Optional[int] = None
    ce_rate: Optional[float] = None
    part_rate: Optional[float] = None
    fa_rate: Optional[float] = None
    dc_rate: Optional[float] = None
    justification: Optional[str] = None


class ParBudgetAnalysisCreate(ParBudgetAnalysisBase):
    pass


class ParBudgetAnalysisUpdate(ParBudgetAnalysisBase):
    justification: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None

    @validator("justification", pre=True, always=True)
    def validate_justification(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class ParBudgetAnalysisFind(
    make_optional(FindBase), make_optional(ParBudgetAnalysisBase)
):
    pass


class ParBudgetAnalysisInfo(
    make_optional(ModelBaseInfo), make_optional(ParBudgetAnalysisBase)
):
    pass


class ParBudgetAnalysisListResponse(FindResult):
    founds: Optional[List[ParBudgetAnalysisInfo]] = None
    search_options: Optional[SearchOptions] = None
