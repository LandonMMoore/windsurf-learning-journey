from typing import Optional

from pydantic import BaseModel

from src.schema.base_schema import ModelBaseInfo, make_optional


class AdditionalFundBase(BaseModel):
    federal_fund_id: Optional[int] = None
    par_budget_analysis_id: Optional[int] = None

    ce: Optional[float] = None
    construction: Optional[float] = None
    feasibility_studies: Optional[float] = None
    design: Optional[float] = None
    rights_of_way: Optional[float] = None
    equipment: Optional[float] = None


class AdditionalFundInfo(
    make_optional(ModelBaseInfo), make_optional(AdditionalFundBase)
):
    pass
