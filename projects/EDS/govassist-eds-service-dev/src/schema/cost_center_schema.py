from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class CostCenterBase(BaseModel):
    cost_center: Optional[str] = None
    cost_center_name: Optional[str] = None
    cost_center_parent1: Optional[str] = None
    cost_center_parent1_desc: Optional[str] = None


class CostCenterCreate(CostCenterBase):
    pass


class CostCenterUpdate(CostCenterBase):
    pass


class CostCenterFind(make_optional(FindBase), make_optional(CostCenterBase)):
    pass


class CostCenterInfo(ModelBaseInfo, CostCenterBase):
    pass


class CostCenterListResponse(FindResult):
    founds: Optional[List[CostCenterInfo]] = None
    search_options: Optional[SearchOptions] = None
