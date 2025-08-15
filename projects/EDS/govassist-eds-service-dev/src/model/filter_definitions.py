from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FilterOperator(str, Enum):
    # String operators
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"

    # Numeric operators
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_EQUALS = "greater_than_equals"
    LESS_THAN_EQUALS = "less_than_equals"
    BETWEEN = "between"

    # Date operators
    BEFORE = "before"
    AFTER = "after"

    # Enum operators
    IN = "in"
    NOT_IN = "not_in"


class FilterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    ENUM = "enum"
    BOOLEAN = "boolean"


class FilterField(BaseModel):
    field: str = Field(..., description="Internal field name")
    label: str = Field(..., description="User-facing label")
    type: FilterType = Field(..., description="Field type")
    operators: List[FilterOperator] = Field(
        ..., description="Allowed operators for this field"
    )
    values: Optional[List[str]] = Field(None, description="Enum values if type is enum")


class FilterDefinitionsResponse(BaseModel):
    fields: List[FilterField] = Field(..., description="List of filterable fields")
