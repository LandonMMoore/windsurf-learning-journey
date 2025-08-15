from typing import List, Optional

from pydantic import BaseModel, Field, validator

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)
from src.schema.budget_items_schema import BudgetItemsInfo


class BudgetInfoBase(BaseModel):
    par_id: Optional[int] = None
    task_name: Optional[str] = None


class BudgetInfoCreate(BudgetInfoBase):
    par_id: int
    task_name: str = Field(min_length=2)

    @validator("task_name", pre=True, always=True)
    def validate_task_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v


class BudgetInfoUpdate(BudgetInfoCreate):
    pass


class BudgetInfoFind(make_optional(FindBase), make_optional(BudgetInfoBase)):
    pass


class BudgetInfoInfo(make_optional(ModelBaseInfo), make_optional(BudgetInfoBase)):
    budget_items: Optional[List[BudgetItemsInfo]] = None


class BudgetInfoListResponse(FindResult):
    founds: Optional[List[BudgetInfoInfo]] = None
    search_options: Optional[SearchOptions] = None


class BudgetInfoParIdInfo(BaseModel):
    par_id: Optional[int] = None
    id: Optional[int] = None


class BudgetInfoTaskNameInfo(BaseModel):
    task_name: Optional[str] = None
    id: Optional[int] = None
