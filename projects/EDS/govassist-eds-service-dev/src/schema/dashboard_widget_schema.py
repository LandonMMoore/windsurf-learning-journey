from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from src.schema.base_schema import (
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class WidgetType(str, Enum):
    NUMBER = "number"
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    STACKED_BAR = "stacked_bar"


class FilterOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    GREATER_THAN_EQUALS = "greater_than_equals"
    LESS_THAN = "less_than"
    LESS_THAN_EQUALS = "less_than_equals"
    BETWEEN = "between"
    RANGE = "range"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IN = "in"
    NOT_IN = "not_in"


class LogicalOperator(str, Enum):
    AND = "and"
    OR = "or"


class FieldCondition(BaseModel):
    """Represents a single field condition with operator and value"""

    operator: FilterOperator
    value: Any
    start: Optional[Any] = None  # For range/between operations
    end: Optional[Any] = None  # For range/between operations


class FilterCondition(BaseModel):
    """Represents a filter condition that can be either a field condition or a logical group"""

    # For field conditions (e.g., {"budget_analyst": {"operator": "equals", "value": "sdfghjk"}})
    field_conditions: Optional[Dict[str, FieldCondition]] = None

    # For logical groups (e.g., {"operator": "and", "conditions": [...]})
    operator: Optional[LogicalOperator] = None
    conditions: Optional[List["FilterCondition"]] = None

    @validator("field_conditions", "operator", "conditions", pre=True, always=True)
    def validate_mutual_exclusivity(cls, v, values):
        """Ensure either field_conditions OR operator+conditions is provided, not both"""
        if "field_conditions" in values and values["field_conditions"] is not None:
            if v is not None:  # This is operator or conditions
                raise ValueError(
                    "Cannot have both field_conditions and logical operator/conditions"
                )
        elif "operator" in values and values["operator"] is not None:
            if (
                v is not None
                and "field_conditions" in values
                and values["field_conditions"] is not None
            ):
                raise ValueError(
                    "Cannot have both field_conditions and logical operator/conditions"
                )
        return v


# Update the FilterCondition class to support forward references
FilterCondition.model_rebuild()


class EnhancedFilters(BaseModel):
    """Enhanced filters schema supporting nested AND/OR operators"""

    operator: LogicalOperator
    conditions: List[FilterCondition]


class DashboardWidgetBase(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = Field(default=None, min_length=2)
    widget_type: str = Field(min_length=1)  # TODO: add enum
    image_url: Optional[str] = Field(default=None)
    data_source: Optional[str] = Field(default=None)
    filters: Optional[dict] = Field(default=None)
    show_legend: bool = Field(default=True)
    x_position: Optional[str] = Field(default=None)
    y_position: Optional[str] = Field(default=None)
    width: Optional[str] = Field(default=None)
    height: Optional[str] = Field(default=None)
    config: Optional[dict] = Field(default=None)
    dashboard_id: int


class FetchedData(BaseModel):
    widget_type: WidgetType
    config: dict
    data_source: str = Field(
        ...,
        description="The data source index to query (e.g., 'r085' or 'r025' or 'r085_v3')",
    )

    @validator("data_source")
    def validate_data_source(cls, v):
        if v not in ["r085", "r025", "r085_v3"]:
            raise ValueError('data_source must be either "r085" or "r025" or "r085_v3"')
        return v

    @validator("config")
    def validate_config_filters(cls, v):
        """Validate that filters in config follow the enhanced schema if present"""
        if isinstance(v, dict) and "filters" in v:
            filters = v["filters"]
            if filters is not None:
                # Try to parse as EnhancedFilters to validate structure
                try:
                    if (
                        isinstance(filters, dict)
                        and "operator" in filters
                        and "conditions" in filters
                    ):
                        EnhancedFilters(**filters)
                except Exception:
                    # If it's not the enhanced format, it might be the old format, which is still valid
                    pass
        return v


class DashboardWidgetCreate(DashboardWidgetBase):
    pass


class DashboardWidgetUpdate(make_optional(DashboardWidgetBase)):
    pass


class WidgetPositionData(BaseModel):
    id: int
    x_position: Optional[str] = None
    y_position: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    show_legend: Optional[bool] = None


class DashboardWidgetBulkUpdate(BaseModel):
    dashboard_id: int
    widgets: List[WidgetPositionData]


class DashboardWidgetFind(BaseModel):
    dashboard_id: int
    pass


class DashboardWidgetInfo(ModelBaseInfo, DashboardWidgetBase):
    """Dashboard widget information with favorite status.

    This class extends the base widget information with a favorite status flag
    that indicates whether the widget is favorited by the current user.
    """

    is_favorite: bool = Field(
        default=False,
        description="Indicates whether this widget is favorited by the current user",
    )

    class Config:
        from_attributes = True


class DashboardWidgetListResponse(FindResult):
    founds: Optional[List[DashboardWidgetInfo]] = None
    search_options: Optional[SearchOptions] = None
