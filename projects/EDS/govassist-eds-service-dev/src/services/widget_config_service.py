from typing import Any, Dict, List, Optional, Union

from loguru import logger

from src.core.exceptions import BadRequestError, InternalServerError
from src.elasticsearch.constants import (
    APPROVED_PAR_CHART_FIELDS,
    APPROVED_R025_CHART_FIELDS,
    BASE_VALIDATION_RULES,
    CHART_CONFIGS,
    FIELD_TYPE_AGGREGATIONS,
    AggregationType,
    ChartType,
    FieldType,
    TimeGranularity,
    get_field_display_name,
)
from src.elasticsearch.models import (
    ChartComponentFields,
    ChartConfig,
    ChartFieldConfig,
    ChartFieldsResponse,
    ChartValidationRule,
    CustomChartConfig,
    FieldMetadata,
    NestedFieldConfig,
)
from src.util.chart_helpers import is_supported_chart_type
from src.util.elasticsearch import (
    build_terms_aggregation_query,
    categorize_fields,
    get_field_mapping,
    get_field_stats_from_es,
    get_field_type,
    get_index_mappings,
)


async def get_validation_rules(
    chart_type: ChartType, index_name: Optional[str] = None
) -> ChartValidationRule:
    """Get validation rules for a chart type"""

    if chart_type not in BASE_VALIDATION_RULES:
        raise ValueError(f"Validation rules for chart type {chart_type} not found")

    rules = BASE_VALIDATION_RULES[chart_type].copy()

    # If index_name is provided, enhance rules based on actual data
    if index_name:
        try:
            # Get index mapping
            mappings = await get_index_mappings(index_name)
            await categorize_fields(mappings)

            # Enhance rules based on actual field data
            # ... (implementation of field-data-specific rule enhancement)
            pass
        except Exception as e:
            # Log the error but continue with base rules
            logger.error(f"Error enhancing validation rules: {str(e)}")

    # Remove duplicates from lists and sort
    for field_role in rules["aggregation_rules"]:
        rules["aggregation_rules"][field_role] = sorted(
            list(set(rules["aggregation_rules"][field_role]))
        )

    return ChartValidationRule(**rules)


async def get_aggregation_templates() -> List[Dict[str, Any]]:
    """Get predefined aggregation templates"""
    return [
        {
            "name": "Year over Year Growth",
            "type": AggregationType.YEAR_OVER_YEAR,
            "requires_date_field": True,
            "parameters": {"comparison_field": "required", "metric": "required"},
        },
        {
            "name": "Moving Average",
            "type": AggregationType.MOVING_AVERAGE,
            "parameters": {"window": 7, "model": "simple"},
        },
        {
            "name": "Weighted Average",
            "type": AggregationType.WEIGHTED_AVERAGE,
            "parameters": {"value_field": "required", "weight_field": "required"},
        },
        {
            "name": "Percentile Distribution",
            "type": AggregationType.PERCENTILE,
            "parameters": {"percents": [25, 50, 75, 95]},
        },
        {
            "name": "Running Total",
            "type": AggregationType.CUMULATIVE_SUM,
            "parameters": {"sort_field": "required"},
        },
    ]


async def get_field_values(
    field_name: str, index_name: str, limit: Optional[int] = 100
) -> List[Union[str, int, float, bool]]:
    """Get possible values for a field with optional limit"""
    from src.elasticsearch.service import es_service

    # Get field mapping to determine type
    mapping = await get_field_mapping(index_name, field_name)
    if not mapping:
        raise ValueError(f"Field {field_name} not found")

    field_type = await get_field_type(mapping)

    # Build query based on field type
    if field_type in [FieldType.TEXT, FieldType.BOOLEAN]:
        logger.info(f"Building terms aggregation query for field: {field_name}")

        # Check if field has keyword mapping or fielddata enabled
        field_info = mapping.get("mapping", {}).get(field_name, {})
        has_keyword = "fields" in field_info and "keyword" in field_info["fields"]
        has_fielddata = field_info.get("fielddata", False)

        if field_type == FieldType.TEXT and not has_keyword and not has_fielddata:
            logger.warning(
                f"Field {field_name} is a text field without keyword mapping or fielddata. Skipping aggregation."
            )
            return []

        # Use appropriate field name for aggregation
        if field_type == FieldType.TEXT and has_keyword:
            agg_field_name = f"{field_name}.keyword"
        else:
            agg_field_name = field_name
            logger.info(f"Using field: {agg_field_name}")

        query = await build_terms_aggregation_query(agg_field_name, limit)

        # Add exists filter to only include documents that have this field
        query["query"] = {"exists": {"field": field_name}}

        try:
            result = await es_service.search(index_name, query)
            values = [
                bucket["key"] for bucket in result["aggregations"]["values"]["buckets"]
            ]
        except Exception as e:
            logger.error(f"Error querying field {field_name}: {str(e)}")
            if (
                "fielddata is disabled" in str(e).lower()
                or "field data" in str(e).lower()
            ):
                logger.warning(
                    f"Field {field_name} doesn't support aggregations. Returning empty list."
                )
                return []
            raise InternalServerError(detail="Internal Server Error")

    elif field_type == FieldType.NUMERIC:
        logger.info(f"Building numeric query for field: {field_name}")
        query = {
            "size": limit,
            "sort": [{field_name: "asc"}],
            "_source": [field_name],
            "query": {"exists": {"field": field_name}},
        }
        result = await es_service.search(index_name, query)
        values = [
            doc["_source"].get(field_name)
            for doc in result["hits"]["hits"]
            if field_name in doc["_source"]
        ]

    else:  # DATE
        logger.info(f"Building date query for field: {field_name}")
        query = {
            "size": limit,
            "sort": [{field_name: "asc"}],
            "_source": [field_name],
            "query": {"exists": {"field": field_name}},
        }

        result = await es_service.search(index_name, query)
        values = [
            doc["_source"].get(field_name)
            for doc in result["hits"]["hits"]
            if field_name in doc["_source"]
        ]
    return values


async def get_available_chart_fields_data(
    chart_type: ChartType, index_name: str
) -> ChartFieldsResponse:
    """Get available fields for different components of a chart type"""

    if not is_supported_chart_type(chart_type):
        raise ValueError(f"Chart type {chart_type} not found or not supported yet")

    # Define APPROVED_CHART_FIELDS based on index name
    approved_chart_fields = (
        APPROVED_R025_CHART_FIELDS
        if index_name == "r025"
        else APPROVED_PAR_CHART_FIELDS
    )

    async def create_field_metadata(
        field_name: str, field_type: FieldType
    ) -> FieldMetadata:
        display_name = get_field_display_name(field_name)
        return FieldMetadata(
            field_name=field_name,
            display_name=display_name,
            field_type=field_type,
            description=f"{field_type.capitalize()} field: {display_name}",
            example_values=None,
            aggregations=None,
        )

    # Create field metadata from approved fields
    numeric_fields = []
    text_fields = []
    keyword_fields = []
    date_fields = []

    for field_key, field_info in approved_chart_fields.items():
        field_name = field_info["field_name"].lower()

        if any(
            numeric_keyword in field_name
            for numeric_keyword in [
                "budget",
                "amount",
                "rate",
                "balance",
                "expenditure",
                "obligation",
                "commitment",
                "total",
                "initial",
                "adjustment",
                "allotment",
            ]
        ):
            numeric_fields.append(
                await create_field_metadata(field_name, FieldType.NUMERIC)
            )
        elif any(
            date_keyword in field_name
            for date_keyword in ["date", "created_at", "updated_at"]
        ):
            date_fields.append(await create_field_metadata(field_name, FieldType.DATE))
        else:
            # Default to keyword for most other fields
            keyword_fields.append(
                await create_field_metadata(field_name, FieldType.KEYWORD)
            )

    # Combine text and keyword fields for category components
    category_fields = text_fields + keyword_fields

    component_field_types = {
        ChartType.BAR: {
            "x_axis": [FieldType.KEYWORD, FieldType.DATE, FieldType.NUMERIC],
            "y_axis": [FieldType.NUMERIC, FieldType.KEYWORD],
            "group_by": [FieldType.KEYWORD],
        },
        ChartType.LINE: {
            "x_axis": [FieldType.DATE, FieldType.KEYWORD, FieldType.NUMERIC],
            "y_axis": [FieldType.NUMERIC, FieldType.KEYWORD],
            "group_by": [FieldType.KEYWORD],
        },
        ChartType.PIE: {
            "value": [FieldType.NUMERIC, FieldType.KEYWORD],
            "category": [FieldType.KEYWORD],
        },
        ChartType.NUMBER: {"value": [FieldType.NUMERIC, FieldType.KEYWORD]},
        ChartType.STACKED_BAR: {
            "x_axis": [FieldType.KEYWORD, FieldType.DATE, FieldType.NUMERIC],
            "y_axis": [FieldType.NUMERIC],
            "stack_by": [FieldType.KEYWORD],
        },
    }

    chart_component_types = component_field_types.get(chart_type, {})

    field_type_map = {
        FieldType.NUMERIC: numeric_fields,
        FieldType.TEXT: text_fields,
        FieldType.KEYWORD: keyword_fields,
        FieldType.DATE: date_fields,
    }

    chart_fields = {
        ChartType.NUMBER: {
            "components": {
                "value": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("value", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[
                        *[f.field_name for f in numeric_fields[:2]],
                        *[f.field_name for f in keyword_fields[:2]],
                    ][:2],
                    required_field_type=None,
                )
            },
            "example_config": {
                "value": numeric_fields[0].field_name if numeric_fields else "",
                "aggregation": "sum",
            },
        },
        ChartType.PIE: {
            "components": {
                "value": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("value", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[
                        *[f.field_name for f in numeric_fields[:2]],
                        *[f.field_name for f in keyword_fields[:2]],
                    ][:2],
                    required_field_type=None,
                ),
                "category": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("category", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[f.field_name for f in category_fields[:2]],
                    required_field_type=None,
                ),
            },
            "example_config": {
                "value": numeric_fields[0].field_name if numeric_fields else "",
                "category": category_fields[0].field_name if category_fields else "",
                "aggregation": "sum",
            },
        },
        ChartType.BAR: {
            "components": {
                "x_axis": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("x_axis", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[
                        *[f.field_name for f in category_fields[:1]],
                        *[f.field_name for f in date_fields[:1]],
                        *[f.field_name for f in numeric_fields[:1]],
                    ][:2],
                    required_field_type=None,
                ),
                "y_axis": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("y_axis", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[
                        *[f.field_name for f in numeric_fields[:2]],
                        *[f.field_name for f in keyword_fields[:2]],
                    ][:2],
                    required_field_type=None,
                ),
                "group_by": ChartComponentFields(
                    available_fields=category_fields,
                    recommended_fields=[f.field_name for f in category_fields[1:2]],
                    required_field_type=FieldType.TEXT,
                ),
            },
            "example_config": {
                "x_axis": (
                    category_fields[0].field_name
                    if category_fields
                    else (
                        date_fields[0].field_name
                        if date_fields
                        else (numeric_fields[0].field_name if numeric_fields else "")
                    )
                ),
                "y_axis": numeric_fields[0].field_name if numeric_fields else "",
                "group_by": (
                    category_fields[1].field_name if len(category_fields) > 1 else ""
                ),
                "aggregation": "sum",
            },
        },
        ChartType.LINE: {
            "components": {
                "x_axis": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("x_axis", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[
                        *[f.field_name for f in date_fields[:1]],
                        *[f.field_name for f in category_fields[:1]],
                        *[f.field_name for f in numeric_fields[:1]],
                    ][:2],
                    required_field_type=None,
                ),
                "y_axis": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("y_axis", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[
                        *[f.field_name for f in numeric_fields[:2]],
                        *[f.field_name for f in keyword_fields[:2]],
                    ][:2],
                    required_field_type=None,
                ),
                "group_by": ChartComponentFields(
                    available_fields=category_fields,
                    recommended_fields=[f.field_name for f in category_fields[:1]],
                    required_field_type=FieldType.TEXT,
                ),
            },
            "example_config": {
                "x_axis": (
                    date_fields[0].field_name
                    if date_fields
                    else (
                        category_fields[0].field_name
                        if category_fields
                        else (numeric_fields[0].field_name if numeric_fields else "")
                    )
                ),
                "y_axis": numeric_fields[0].field_name if numeric_fields else "",
                "group_by": category_fields[0].field_name if category_fields else "",
                "aggregation": "sum",
            },
        },
        ChartType.STACKED_BAR: {
            "components": {
                "x_axis": ChartComponentFields(
                    available_fields=[
                        field
                        for field_type in chart_component_types.get("x_axis", [])
                        for field in field_type_map.get(field_type, [])
                    ],
                    recommended_fields=[
                        *[f.field_name for f in category_fields[:1]],
                        *[f.field_name for f in date_fields[:1]],
                        *[f.field_name for f in numeric_fields[:1]],
                    ][:2],
                    required_field_type=None,
                ),
                "y_axis": ChartComponentFields(
                    available_fields=numeric_fields,
                    recommended_fields=[
                        *[f.field_name for f in numeric_fields[:2]],
                    ],
                    required_field_type=FieldType.NUMERIC,
                ),
                "stack_by": ChartComponentFields(
                    available_fields=category_fields,
                    recommended_fields=[f.field_name for f in category_fields[:1]],
                    required_field_type=FieldType.TEXT,
                ),
            },
            "example_config": {
                "x_axis": (
                    category_fields[0].field_name
                    if category_fields
                    else (
                        date_fields[0].field_name
                        if date_fields
                        else (numeric_fields[0].field_name if numeric_fields else "")
                    )
                ),
                "y_axis": numeric_fields[0].field_name if numeric_fields else "",
                "stack_by": category_fields[0].field_name if category_fields else "",
                "aggregation": "sum",
            },
        },
    }

    return ChartFieldsResponse(**chart_fields[chart_type])


async def get_nested_fields(index_name: str) -> List[NestedFieldConfig]:
    """Get available nested fields and their configurations"""
    from src.elasticsearch.service import es_service

    # Get index mapping
    mapping = await es_service.client.indices.get_mapping(index=index_name)
    properties = mapping[index_name]["mappings"]["properties"]

    nested_fields = []

    for field_name, field_info in properties.items():
        if field_info.get("type") == "nested":
            nested_properties = field_info.get("properties", {})
            nested_fields.append(
                NestedFieldConfig(
                    path=field_name,
                    fields=list(nested_properties.keys()),
                    aggregations=[
                        AggregationType.COUNT,
                        AggregationType.SUM,
                        AggregationType.AVG,
                    ],
                )
            )

    return nested_fields


async def validate_chart_config(config: CustomChartConfig) -> Dict[str, Any]:
    """Validate a custom chart configuration"""
    validation_rules = await get_validation_rules(config.chart_type)

    errors = []

    # Check required fields
    for field in validation_rules.required_fields:
        if field not in config.fields:
            errors.append(f"Missing required field: {field}")

    # Check incompatible fields
    for incompatible_set in validation_rules.incompatible_fields:
        if all(field in config.fields for field in incompatible_set):
            errors.append(f"Incompatible fields used together: {incompatible_set}")

    # Check dependent fields
    for field, dependencies in validation_rules.dependent_fields.items():
        if field in config.fields:
            for dep in dependencies:
                if dep not in config.fields:
                    errors.append(f"Field {field} requires {dep}")

    # Check aggregation rules
    for field, allowed_aggs in validation_rules.aggregation_rules.items():
        if field in config.fields:
            for agg in config.aggregations:
                if agg.field == config.fields[field] and agg.type not in allowed_aggs:
                    errors.append(f"Invalid aggregation {agg.type} for field {field}")

    return {"is_valid": len(errors) == 0, "errors": errors}


async def preview_chart_data(
    config: CustomChartConfig, index_name: str, sample_size: int = 1000
) -> Dict[str, Any]:
    """Preview data for a custom chart configuration"""
    from src.elasticsearch.service import es_service
    from src.util.chart_helpers import build_chart_preview_query, transform_aggregations

    # Validate the config
    validation_result = await validate_chart_config(config)
    if not validation_result["is_valid"]:
        return {
            "error": "Invalid chart configuration",
            "details": validation_result["errors"],
        }

    # Convert the advanced aggregations to simple format for the query builder
    aggregations = transform_aggregations(config.aggregations)

    # Build the query using the helper
    try:
        query = await build_chart_preview_query(
            config.chart_type,
            config.fields,
            aggregations,
            config.filters,
            config.time_granularity,
        )

        # Add any custom handling for nested fields if needed
        if config.nested_fields:
            for nested_config in config.nested_fields:
                for agg in config.aggregations:
                    if agg.field.startswith(f"{nested_config.path}."):
                        query["aggs"][f"{nested_config.path}_agg"] = {
                            "nested": {"path": nested_config.path},
                            "aggs": {
                                f"{agg.type}_{agg.field}": {
                                    agg.type: {"field": agg.field}
                                }
                            },
                        }

        # Execute the query
        result = await es_service.search(index_name, query)

        return {
            "aggregations": result["aggregations"],
            "total_records": result["hits"]["total"]["value"],
        }
    except Exception:
        return {"error": "Error generating chart preview"}


async def get_field_stats(
    field_name: str, index_name: str
) -> Dict[str, Union[int, float, str, List[Union[int, float, str]]]]:
    """Get field statistics for dashboard widgets"""
    # Get field mapping
    mapping = await get_field_mapping(index_name, field_name)
    if not mapping:
        raise ValueError(f"Field {field_name} not found")

    # Get field type and stats
    field_type = await get_field_type(mapping)
    stats = await get_field_stats_from_es(index_name, field_name, field_type)

    # Process stats based on field type
    result = {}

    if field_type == FieldType.NUMERIC:
        result = {
            "type": "numeric",
            "min": stats["field_stats"]["min"],
            "max": stats["field_stats"]["max"],
            "avg": stats["field_stats"]["avg"],
            "count": stats["field_stats"]["count"],
            "common_values": [
                b["key"] for b in stats.get("common_values", {}).get("buckets", [])
            ],
        }
    elif field_type == FieldType.DATE:
        result = {
            "type": "date",
            "min": stats["min_date"]["value_as_string"],
            "max": stats["max_date"]["value_as_string"],
            "count": stats["distinct_count"]["value"],
        }
    else:
        result = {
            "type": "text",
            "distinct_count": stats["distinct_count"]["value"],
            "common_values": [
                b["key"] for b in stats.get("common_values", {}).get("buckets", [])
            ],
        }

    return result


async def get_time_granularities(
    index_name: Optional[str] = None, field_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get available time granularities and their configurations.
    If index_name and field_name are provided, it will suggest granularities based on the data.
    """
    # Base time granularities
    granularities = [
        {
            "id": TimeGranularity.YEAR,
            "name": "Year",
            "description": "Group data by year",
            "date_format": "yyyy",
            "interval": "1y",
        },
        {
            "id": TimeGranularity.QUARTER,
            "name": "Quarter",
            "description": "Group data by quarter",
            "date_format": "yyyy-QQ",
            "interval": "1q",
        },
        {
            "id": TimeGranularity.MONTH,
            "name": "Month",
            "description": "Group data by month",
            "date_format": "yyyy-MM",
            "interval": "1M",
        },
        {
            "id": TimeGranularity.WEEK,
            "name": "Week",
            "description": "Group data by week",
            "date_format": "yyyy-ww",
            "interval": "1w",
        },
        {
            "id": TimeGranularity.DAY,
            "name": "Day",
            "description": "Group data by day",
            "date_format": "yyyy-MM-dd",
            "interval": "1d",
        },
        {
            "id": TimeGranularity.HOUR,
            "name": "Hour",
            "description": "Group data by hour",
            "date_format": "yyyy-MM-dd HH",
            "interval": "1h",
        },
        {
            "id": TimeGranularity.MINUTE,
            "name": "Minute",
            "description": "Group data by minute",
            "date_format": "yyyy-MM-dd HH:mm",
            "interval": "1m",
        },
    ]

    # If index_name and field_name are provided, enhance with data-specific info
    if index_name and field_name:
        try:
            # Get field mapping
            mapping = await get_field_mapping(index_name, field_name)
            if not mapping:
                return granularities

            # Check if it's a date field
            field_type = await get_field_type(mapping)
            if field_type != FieldType.DATE:
                raise ValueError(f"Field {field_name} is not a date field")

            # Get field statistics
            stats = await get_field_stats_from_es(index_name, field_name, field_type)

            min_date = stats.get("min_date", {}).get("value_as_string", "")
            max_date = stats.get("max_date", {}).get("value_as_string", "")

            # Calculate date range and recommend appropriate granularities
            if min_date and max_date:
                from datetime import datetime

                min_dt = datetime.strptime(min_date.split("T")[0], "%Y-%m-%d")
                max_dt = datetime.strptime(max_date.split("T")[0], "%Y-%m-%d")

                date_diff = (max_dt - min_dt).days

                # Mark recommended granularities based on date range
                for granularity in granularities:
                    if date_diff > 365 * 5 and granularity["id"] in [
                        TimeGranularity.YEAR,
                        TimeGranularity.QUARTER,
                    ]:
                        granularity["recommended"] = True
                    elif date_diff > 365 and granularity["id"] in [
                        TimeGranularity.QUARTER,
                        TimeGranularity.MONTH,
                    ]:
                        granularity["recommended"] = True
                    elif date_diff > 90 and granularity["id"] in [
                        TimeGranularity.MONTH,
                        TimeGranularity.WEEK,
                    ]:
                        granularity["recommended"] = True
                    elif date_diff > 30 and granularity["id"] in [
                        TimeGranularity.WEEK,
                        TimeGranularity.DAY,
                    ]:
                        granularity["recommended"] = True
                    elif date_diff > 7 and granularity["id"] == TimeGranularity.DAY:
                        granularity["recommended"] = True
                    elif date_diff <= 7 and granularity["id"] in [
                        TimeGranularity.HOUR,
                        TimeGranularity.MINUTE,
                    ]:
                        granularity["recommended"] = True
                    else:
                        granularity["recommended"] = False

                # Add date range info
                for granularity in granularities:
                    granularity["date_range"] = {
                        "min": min_date,
                        "max": max_date,
                        "days": date_diff,
                    }

        except Exception:
            # On error, just return the base granularities
            pass

    return granularities


def safe_format_float(value, format_spec=":.2f"):
    """Safely format a value that might be None as a float with the given format spec."""
    if value is None:
        return "N/A"
    return f"{value:{format_spec}}"


def create_generic_example_config(chart_type: ChartType) -> Dict[str, str]:
    """Create a generic example configuration for a chart type"""
    config = {}

    if chart_type == ChartType.BAR:
        config = {
            "x_axis": "category_field",
            "y_axis": "numeric_field",
            "group_by": "group_field",
            "aggregation": "sum",
        }
    elif chart_type == ChartType.LINE:
        config = {
            "x_axis": "date_field",
            "y_axis": "numeric_field",
            "group_by": "group_field",
            "aggregation": "sum",
        }
    elif chart_type == ChartType.PIE:
        config = {
            "category": "category_field",
            "value": "numeric_field",
            "aggregation": "sum",
        }
    elif chart_type == ChartType.NUMBER:
        config = {"value": "numeric_field", "aggregation": "sum"}

    return config


async def get_chart_config_data(
    chart_type: ChartType, index_name: Optional[str] = None
) -> ChartConfig:
    """Get configuration options for a specific chart type"""
    if chart_type not in CHART_CONFIGS:
        raise ValueError(f"Chart type {chart_type} not found")

    config = CHART_CONFIGS[chart_type].copy()

    # Define component field type mappings based on chart type
    component_field_types = {
        ChartType.BAR: {
            "x_axis": [FieldType.KEYWORD, FieldType.DATE, FieldType.NUMERIC],
            "y_axis": [FieldType.NUMERIC, FieldType.KEYWORD],
            "group_by": [FieldType.KEYWORD],
        },
        ChartType.LINE: {
            "x_axis": [FieldType.DATE, FieldType.KEYWORD, FieldType.NUMERIC],
            "y_axis": [FieldType.NUMERIC, FieldType.KEYWORD],
            "group_by": [FieldType.KEYWORD],
        },
        ChartType.PIE: {"value": [FieldType.NUMERIC], "category": [FieldType.KEYWORD]},
        ChartType.NUMBER: {"value": [FieldType.NUMERIC]},
        ChartType.STACKED_BAR: {
            "x_axis": [FieldType.KEYWORD, FieldType.DATE, FieldType.NUMERIC],
            "y_axis": [FieldType.NUMERIC],
            "stack_by": [FieldType.KEYWORD],
        },
    }

    config["component_field_types"] = component_field_types.get(chart_type, {})

    # If index_name is provided, enhance with actual data examples
    if index_name:
        try:
            from src.elasticsearch.service import es_service

            mapping = await es_service.client.indices.get_mapping(index=index_name)
            fields_mapping = mapping[index_name]["mappings"]["properties"]

            example_fields = {}
            for field_name, field_info in fields_mapping.items():
                # Skip if field is not in the approved list
                if field_name not in APPROVED_PAR_CHART_FIELDS:
                    continue

                es_type = field_info.get("type")
                if es_type in ["long", "integer", "short", "byte", "double", "float"]:
                    example_fields.setdefault("numeric", []).append(field_name)
                elif es_type in ["text", "keyword"]:
                    example_fields.setdefault("text", []).append(field_name)
                elif es_type == "date":
                    example_fields.setdefault("date", []).append(field_name)

            # Build example config with actual fields
            example_config = {}

            # Process required fields
            for field_role, field_type in config["required_fields"].items():
                if field_role in config["component_field_types"]:
                    for supported_type in config["component_field_types"][field_role]:
                        if supported_type == FieldType.NUMERIC and example_fields.get(
                            "numeric"
                        ):
                            example_config[field_role] = example_fields["numeric"][0]
                            break
                        elif supported_type == FieldType.TEXT and example_fields.get(
                            "text"
                        ):
                            example_config[field_role] = example_fields["text"][0]
                            break
                        elif supported_type == FieldType.DATE and example_fields.get(
                            "date"
                        ):
                            example_config[field_role] = example_fields["date"][0]
                            break
                else:
                    type_map = {
                        "numeric": FieldType.NUMERIC,
                        "text": FieldType.TEXT,
                        "date": FieldType.DATE,
                    }
                    for es_type, field_type_enum in type_map.items():
                        if field_type == field_type_enum and example_fields.get(
                            es_type
                        ):
                            example_config[field_role] = example_fields[es_type][0]
                            break

            # Process optional fields
            for field_role, field_type in config["optional_fields"].items():
                if field_role in config["component_field_types"]:
                    for supported_type in config["component_field_types"][field_role]:
                        field_list = example_fields.get(supported_type.value, [])
                        if field_list and len(field_list) > 1:
                            example_config[field_role] = field_list[1]
                            break
                        elif field_list:
                            example_config[field_role] = field_list[0]
                            break

            # Add default aggregation
            if "y_axis" in example_config or "value" in example_config:
                example_config["aggregation"] = "sum"

            config["example_config"] = example_config

        except Exception as e:
            logger.warning(f"Error getting field information: {str(e)}")
            config["example_config"] = create_generic_example_config(chart_type)
    else:
        config["example_config"] = create_generic_example_config(chart_type)

    return ChartConfig(**config)


async def get_field_config_data(field_name: str, index_name: str) -> ChartFieldConfig:
    """Get configuration and metadata for a specific field"""
    # Check if field is in approved list
    if field_name not in APPROVED_PAR_CHART_FIELDS:
        raise ValueError(f"Field {field_name} is not approved for chart creation")

    # Get field mapping from Elasticsearch
    mapping = await get_field_mapping(index_name, field_name)
    if not mapping:
        raise ValueError(f"Field {field_name} not found")

    # Get field type
    field_type = await get_field_type(mapping)

    # Get field statistics from Elasticsearch
    field_stats = await get_field_stats_from_es(index_name, field_name, field_type)

    # Configure supported aggregations based on field type
    supported_aggregations = FIELD_TYPE_AGGREGATIONS.get(
        field_type, [AggregationType.COUNT]
    )
    suggested_values = []

    if field_type == FieldType.NUMERIC:
        # Check if there was an error with the field
        if "error" in field_stats:
            description = f"Numeric field with limited aggregation support: {field_stats['error']}"
            supported_aggregations = [AggregationType.COUNT]
        else:
            # Get suggested values from stats
            suggested_values = [
                bucket["key"]
                for bucket in field_stats.get("common_values", {}).get("buckets", [])
            ]
            min_val = field_stats["field_stats"].get("min")
            max_val = field_stats["field_stats"].get("max")
            avg_val = field_stats["field_stats"].get("avg")

            description = (
                f"Numeric field with range [{safe_format_float(min_val)} "
                f"to {safe_format_float(max_val)}], "
                f"average: {safe_format_float(avg_val)}"
            )

    elif field_type == FieldType.DATE:
        if "error" in field_stats:
            description = (
                f"Date field with limited aggregation support: {field_stats['error']}"
            )
            supported_aggregations = [AggregationType.COUNT]
        else:
            suggested_values = [
                field_stats["min_date"]["value_as_string"],
                field_stats["max_date"]["value_as_string"],
            ]
            description = (
                f"Date field ranging from {field_stats['min_date']['value_as_string']} "
                f"to {field_stats['max_date']['value_as_string']}"
            )

    else:  # TEXT or other types
        # Check if there was an error with the text field
        if "error" in field_stats:
            description = (
                f"Text field with limited aggregation support: {field_stats['error']}"
            )
            supported_aggregations = [AggregationType.COUNT]
        else:
            suggested_values = [
                bucket["key"]
                for bucket in field_stats.get("common_values", {}).get("buckets", [])
            ]
            description = (
                f"Text field with {field_stats['distinct_count']['value']} "
                "distinct values"
            )

    return ChartFieldConfig(
        field_name=field_name,
        display_name=get_field_display_name(field_name),
        field_type=field_type,
        supported_aggregations=supported_aggregations,
        suggested_values=suggested_values,
        description=description,
    )


async def get_fields_by_data_types_data(
    index_name: str,
    data_types: Optional[List[FieldType]] = None,
) -> Dict[FieldType, List[str]]:
    """Get fields from an index filtered by specific data types"""

    # Select the appropriate approved fields based on index
    selected_approved_fields = (
        APPROVED_R025_CHART_FIELDS
        if index_name == "r025"
        else APPROVED_PAR_CHART_FIELDS
    )

    # Get all approved field names for easier lookup
    approved_field_names = [
        info["field_name"] for info in selected_approved_fields.values()
    ]
    mappings = await get_index_mappings(index_name)
    categorized_fields = await categorize_fields(mappings)

    result = {}
    type_mapping = {
        "text": FieldType.TEXT,
        "keyword": FieldType.KEYWORD,
        "numeric": FieldType.NUMERIC,  # Add the categorized field name
        "long": FieldType.NUMERIC,
        "integer": FieldType.NUMERIC,
        "short": FieldType.NUMERIC,
        "byte": FieldType.NUMERIC,
        "double": FieldType.NUMERIC,
        "float": FieldType.NUMERIC,
        "date": FieldType.DATE,
        "boolean": FieldType.BOOLEAN,
        "nested": FieldType.NESTED,
        "object": FieldType.OBJECT,
        "geo_point": FieldType.GEO_POINT,
        "ip": FieldType.IP,
    }

    # If data_types not provided, return all categorized fields
    if not data_types:
        for category, fields in categorized_fields.items():
            field_type = type_mapping.get(category)
            if field_type:
                # Filter by approved fields
                approved_fields = [
                    field for field in fields if field in approved_field_names
                ]
                if approved_fields:
                    result[field_type] = approved_fields
    else:
        # Filter fields based on requested data types
        for category, fields in categorized_fields.items():
            field_type = type_mapping.get(category)

            if field_type and field_type in data_types:
                # Filter by approved fields
                approved_fields = [
                    field for field in fields if field in approved_field_names
                ]

                if approved_fields:
                    result[field_type] = approved_fields

    return result


async def get_field_aggregations_data(
    field_type: FieldType,
) -> List[AggregationType]:
    """Get available aggregations for a field type"""

    if field_type not in FIELD_TYPE_AGGREGATIONS:
        raise BadRequestError(f"Unsupported field type: {field_type.value}")

    aggregations = FIELD_TYPE_AGGREGATIONS[field_type]

    # Remove duplicates and sort
    return list(set(aggregations))


async def get_field_values_data(
    field_name: str, index_name: str, limit: Optional[int] = 100
) -> List[Union[str, int, float, bool]]:
    """Get possible values for a field with optional limit with permission check"""

    # Select the appropriate approved fields based on index
    approved_fields = (
        APPROVED_R025_CHART_FIELDS
        if index_name == "r025"
        else APPROVED_PAR_CHART_FIELDS
    )

    # Get all approved field names for easier lookup
    approved_field_names = [
        field_info["field_name"] for field_info in approved_fields.values()
    ]

    # Check if field is in approved list
    if field_name not in approved_field_names:
        raise ValueError(f"Field {field_name} is not approved for chart creation")

    return await get_field_values(field_name, index_name, limit)


async def get_field_stats_data(
    field_name: str, index_name: str
) -> Dict[str, Union[int, float, str, List[Union[int, float, str]]]]:
    """Get statistical information about a field with permission check"""

    # Select the appropriate approved fields based on index
    approved_fields = (
        APPROVED_R025_CHART_FIELDS
        if index_name == "r025"
        else APPROVED_PAR_CHART_FIELDS
    )

    # Get all approved field names for easier lookup
    approved_field_names = [
        field_info["field_name"] for field_info in approved_fields.values()
    ]

    # Check if field is in approved list
    if field_name not in approved_field_names:
        raise ValueError(f"Field {field_name} is not approved for chart creation")

    return await get_field_stats(field_name, index_name)
