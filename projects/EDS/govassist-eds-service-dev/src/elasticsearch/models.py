from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from src.elasticsearch.constants import (
    AggregationType,
    ChartType,
    FieldType,
    TimeGranularity,
)


class ValidationRule(BaseModel):
    rule_type: str
    parameters: Dict[str, Any]
    error_message: str


class ChartValidationRule(BaseModel):
    required_fields: List[str]
    incompatible_fields: List[List[str]]
    dependent_fields: Dict[str, List[str]]
    field_combinations: List[List[str]]
    aggregation_rules: Dict[str, List[AggregationType]]
    time_granularity_rules: Dict[str, List[TimeGranularity]]


class AdvancedAggregation(BaseModel):
    type: AggregationType
    field: str
    parameters: Optional[Dict[str, Any]] = None
    time_granularity: Optional[TimeGranularity] = None
    filters: Optional[Dict[str, Any]] = None
    script: Optional[str] = None


class NestedFieldConfig(BaseModel):
    path: str
    fields: List[str]
    aggregations: List[AggregationType]


class CustomChartConfig(BaseModel):
    chart_type: ChartType
    fields: Dict[str, str]
    aggregations: List[AdvancedAggregation]
    filters: Optional[Dict[str, Any]] = None
    nested_fields: Optional[List[NestedFieldConfig]] = None
    time_granularity: Optional[TimeGranularity] = None
    sorting: Optional[Dict[str, str]] = None
    limit: Optional[int] = None


class FieldMetadata(BaseModel):
    field_name: str
    display_name: str
    field_type: FieldType
    description: Optional[str] = None
    example_values: Optional[List[Union[str, int, float, bool]]] = None
    aggregations: Optional[List[AggregationType]] = None


class ChartComponentFields(BaseModel):
    available_fields: List[FieldMetadata]
    recommended_fields: Optional[List[str]] = None
    required_field_type: Optional[FieldType] = None


class ChartFieldsResponse(BaseModel):
    components: Dict[str, ChartComponentFields]
    example_config: Dict[str, str]


class ChartFieldConfig(BaseModel):
    field_name: str
    display_name: str
    field_type: FieldType
    supported_aggregations: List[AggregationType]
    suggested_values: Optional[List[Union[str, int, float]]] = None
    description: Optional[str] = None


class ChartConfig(BaseModel):
    chart_type: ChartType
    supported_field_types: List[FieldType]
    required_fields: Dict[str, Union[FieldType, List[FieldType]]]
    optional_fields: Dict[str, Union[FieldType, List[FieldType]]]
    supported_aggregations: List[AggregationType]
    example_config: Dict
    component_field_types: Optional[Dict[str, List[FieldType]]] = None
