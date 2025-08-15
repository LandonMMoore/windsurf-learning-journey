from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, field_validator

from src.schema.base_schema import FindBase, ModelBaseInfo, make_optional


class fieldCondition(BaseModel):
    operator: str
    value: Any


# class ConditionItem(BaseModel):
#     field: dict[str, fieldCondition]

# @field_validator("field", "operator")
# @classmethod
# def non_empty_str(cls, v: str) -> str:
#     if not isinstance(v, str) or not v.strip():
#         raise ValueError("Field must be a non-empty string")
#     return v


class FilterConfigurationBase(BaseModel):
    # fields: Optional[List[str]] = None
    conditions: List[dict[str, fieldCondition]]
    operator: Optional[str] = None

    # @field_validator("fields")
    # @classmethod
    # def validate_fields(cls, v: List[str]) -> List[str]:
    #     if not isinstance(v, list) or not v:
    #         raise ValueError("fields must be a non-empty list of strings")
    #     for item in v:
    #         if not isinstance(item, str) or not item.strip():
    #             raise ValueError("Each item in 'fields' must be a non-empty string")
    #     return v

    # @field_validator("conditions")
    # @classmethod
    # def validate_conditions(cls, v: List[ConditionItem]) -> List[ConditionItem]:
    #     if not v or not isinstance(v, list):
    #         raise ValueError("conditions must be a non-empty list")
    #     return v

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        valid_operators = ["and", "or", "not"]
        v_lower = v.lower()
        if v_lower not in valid_operators:
            raise ValueError(f"'operator' must be one of {valid_operators}")
        return v_lower


class ParDashboardFilterConfigurationsBaseSchema(BaseModel):
    filter_name: str
    # TODO: Remove any Type later
    filter_configuration: Union[
        dict[str, Union[dict[str, FilterConfigurationBase], str]], None, Any
    ]

    @field_validator("filter_name")
    @classmethod
    def validate_filter_name(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("filter_name must be a non-empty string")
        return v


class ParDashboardFilterConfigurationsCreate(
    ParDashboardFilterConfigurationsBaseSchema
):
    pass


class ParDashboardFilterConfigurationsUpdate(
    make_optional(ParDashboardFilterConfigurationsBaseSchema)
):
    pass


class ParDashboardFilterConfigurationsInfo(
    ModelBaseInfo, ParDashboardFilterConfigurationsBaseSchema
):
    pass


class ParDashboardFilterConfigurationsFind(FindBase):
    """Simple find schema for GET list endpoint - only includes basic search parameters"""

    filter_name: Optional[str] = None


class ParDashboardFilterConfigurationsListResponse(BaseModel):
    founds: List[ParDashboardFilterConfigurationsInfo]
    search_options: Dict[str, Any]
