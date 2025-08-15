from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class FundItem(BaseModel):
    fund_id: int
    fund_type: str
    ce: Optional[float] = None
    construction: Optional[float] = None
    feasibility_studies: Optional[float] = None
    design: Optional[float] = None
    rights_of_way: Optional[float] = None
    equipment: Optional[float] = None


class BudgetAnalysisFundRequest(BaseModel):
    par_id: int
    difs_id: str
    part_rate: float
    fa: float
    dc: float
    justification: Optional[str] = None
    funds: List[FundItem]


class BudgetAnalysisFundBase(BaseModel):
    federal_fund_id: Optional[int] = None
    par_budget_id: Optional[int] = None
    fund_type: Optional[str] = None
    ce: Optional[float] = None
    construction: Optional[float] = None
    feasibility_studies: Optional[float] = None
    design: Optional[float] = None
    rights_of_way: Optional[float] = None
    equipment: Optional[float] = None


class BudgetAnalysisFundDelete(BaseModel):
    budget_analysis_id: int
    FA_fund_id: int
    DC_fund_id: int


class BudgetAnalysisFundCreate(make_optional(BudgetAnalysisFundBase)):
    pass


class BudgetAnalysisFundUpdate(make_optional(BudgetAnalysisFundBase)):
    pass


class BudgetAnalysisFundFind(
    make_optional(FindBase), make_optional(BudgetAnalysisFundBase)
):
    pass


class BudgetAnalysisFundInfo(
    make_optional(ModelBaseInfo), make_optional(BudgetAnalysisFundBase)
):
    pass


class BudgetAnalysisFundListResponse(FindResult):
    founds: Optional[List[BudgetAnalysisFundInfo]] = None
    search_options: Optional[SearchOptions] = None
