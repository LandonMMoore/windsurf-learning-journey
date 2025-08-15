from typing import List, Optional

from pydantic import BaseModel, field_validator

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)
from src.util.regex_validator import (
    non_negative_number_validator,
    not_only_spaces_validator,
)

ALPHANUMERIC_PATTERN = r"^[a-zA-Z0-9\s.,\-()&_/]+$"


class BudgetItemsBase(BaseModel):
    account: str
    parent_task_number: Optional[str] = None
    parent_task_name: Optional[str] = None
    subtask_number: Optional[str] = None
    lifetime_budget: Optional[float] = None
    initial_allotment: Optional[float] = None
    expenditures: Optional[float] = None
    obligations: Optional[float] = None
    commitments: Optional[float] = None
    current_balance: Optional[float] = None
    lifetime_balance: Optional[float] = None
    proposed_budget: Optional[float] = None
    change_amount: Optional[float] = None
    budget_info_id: Optional[int] = None
    comment: Optional[str] = None


class BudgetItemsCreate(BudgetItemsBase):
    budget_info_id: int
    account: str
    parent_task_number: Optional[str] = None
    parent_task_name: Optional[str] = None
    subtask_number: Optional[str] = None
    comment: Optional[str] = None

    @field_validator("account")
    @classmethod
    def validate_account(cls, v):
        return not_only_spaces_validator(
            "Account must not be empty or whitespace only"
        )(cls, v)

    @field_validator("proposed_budget")
    @classmethod
    def validate_proposed_budget(cls, v):
        return non_negative_number_validator("Proposed budget cannot be negative")(
            cls, v
        )


class BudgetItemsUpdate(BudgetItemsBase):
    account: Optional[str] = None
    parent_task_number: Optional[str] = None
    parent_task_name: Optional[str] = None
    subtask_number: Optional[str] = None
    comment: Optional[str] = None

    @field_validator("account")
    @classmethod
    def validate_account(cls, v):
        return not_only_spaces_validator(
            "Account must not be empty or whitespace only"
        )(cls, v)

    @field_validator("proposed_budget")
    @classmethod
    def validate_proposed_budget(cls, v):
        return non_negative_number_validator("Proposed budget cannot be negative")(
            cls, v
        )


class BudgetItemsFind(make_optional(FindBase), make_optional(BudgetItemsBase)):
    pass


class BudgetItemsInfo(ModelBaseInfo, BudgetItemsBase):
    pass


class BudgetItemsListResponse(FindResult):
    founds: Optional[List[BudgetItemsInfo]] = None
    search_options: Optional[SearchOptions] = None
