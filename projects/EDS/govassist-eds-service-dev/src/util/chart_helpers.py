from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from src.elasticsearch.constants import (
    CHART_CONFIGS,
    AggregationType,
    ChartType,
    FieldType,
    TimeGranularity,
)
from src.elasticsearch.models import AdvancedAggregation, FieldMetadata
from src.elasticsearch.service import es_service
from src.util.elasticsearch import (
    build_field_stats_query,
    get_field_examples,
    get_field_mapping,
)


def is_supported_chart_type(chart_type: ChartType) -> bool:
    """Check if a chart type is supported by the application"""
    return chart_type in CHART_CONFIGS


def get_chart_field_types(chart_type: ChartType) -> Dict[str, FieldType]:
    """Get the expected field types for a chart type"""

    if not is_supported_chart_type(chart_type):
        raise ValueError(f"Unsupported chart type: {chart_type}")

    chart_config = CHART_CONFIGS[chart_type]
    return {**chart_config["required_fields"], **chart_config["optional_fields"]}


async def get_suitable_fields_for_chart(
    chart_type: ChartType, index_name: str, categorized_fields: Dict[str, List[str]]
) -> Tuple[List[FieldMetadata], List[FieldMetadata], List[FieldMetadata]]:
    """Get suitable fields for a chart type based on field categories"""
    field_types = get_chart_field_types(chart_type)
    numeric_needed = any(ft == FieldType.NUMERIC for ft in field_types.values())
    text_needed = any(ft == FieldType.TEXT for ft in field_types.values())
    date_needed = any(ft == FieldType.DATE for ft in field_types.values())

    numeric_fields = []
    text_fields = []
    date_fields = []

    # Process numeric fields if needed
    if numeric_needed and categorized_fields.get("numeric"):
        for field_name in categorized_fields["numeric"]:
            try:
                example_values = await get_field_examples(
                    index_name, field_name, FieldType.NUMERIC, 5
                )
                numeric_fields.append(
                    FieldMetadata(
                        field_name=field_name,
                        field_type=FieldType.NUMERIC,
                        description=f"Numeric field: {field_name}",
                        example_values=example_values,
                        aggregations=[
                            AggregationType.SUM,
                            AggregationType.AVG,
                            AggregationType.MIN,
                            AggregationType.MAX,
                        ],
                    )
                )
            except Exception as e:
                logger.warning(
                    f"Skipping numeric field {field_name} due to error: {str(e)}"
                )
                continue

    # Process text fields if needed
    if text_needed and categorized_fields.get("text"):
        for field_name in categorized_fields["text"]:
            try:
                # Check if field has keyword mapping or fielddata enabled
                mapping = await get_field_mapping(index_name, field_name)
                if not mapping:
                    logger.warning(
                        f"Field {field_name} not found in mapping. Skipping."
                    )
                    continue

                field_info = mapping.get("mapping", {}).get(field_name, {})
                has_keyword = (
                    "fields" in field_info and "keyword" in field_info["fields"]
                )
                has_fielddata = field_info.get("fielddata", False)

                # Skip text fields without keyword or fielddata
                if not has_keyword and not has_fielddata:
                    logger.warning(
                        f"Field {field_name} is a text field without keyword mapping or fielddata. Skipping."
                    )
                    continue

                example_values = await get_field_examples(
                    index_name, field_name, FieldType.TEXT, 5
                )

                text_fields.append(
                    FieldMetadata(
                        field_name=field_name,
                        field_type=FieldType.TEXT,
                        description=f"Text field: {field_name}",
                        example_values=example_values,
                        aggregations=[
                            AggregationType.COUNT,
                            AggregationType.DISTINCT_COUNT,
                        ],
                    )
                )
            except Exception as e:
                logger.warning(
                    f"Skipping text field {field_name} due to error: {str(e)}"
                )
                continue

    # Process date fields if needed
    if date_needed and categorized_fields.get("date"):
        for field_name in categorized_fields["date"]:
            try:
                date_query = await build_field_stats_query(field_name, FieldType.DATE)
                date_stats = await es_service.search(index_name, date_query)

                date_fields.append(
                    FieldMetadata(
                        field_name=field_name,
                        field_type=FieldType.DATE,
                        description=f"Date field: {field_name}",
                        example_values=[
                            date_stats["aggregations"]["min_date"]["value_as_string"],
                            date_stats["aggregations"]["max_date"]["value_as_string"],
                        ],
                        aggregations=[AggregationType.MIN, AggregationType.MAX],
                    )
                )
            except Exception as e:
                logger.warning(
                    f"Skipping date field {field_name} due to error: {str(e)}"
                )
                continue

    return numeric_fields, text_fields, date_fields


async def build_chart_preview_query(
    chart_type: ChartType,
    fields: Dict[str, str],
    aggregations: List[Dict[str, Any]],
    filters: Optional[Dict[str, Any]] = None,
    time_granularity: Optional[TimeGranularity] = None,
) -> Dict[str, Any]:
    """Build an Elasticsearch query for chart preview based on chart type and configuration"""
    query = {"size": 0, "aggs": {}}

    # Add filters if provided
    if filters:
        query["query"] = {"bool": {"must": filters}}

    # Handle different chart types
    if chart_type == ChartType.BAR:
        # For bar charts, aggregate by x_axis
        x_field = fields.get("x_axis")
        y_field = fields.get("y_axis")
        group_by = fields.get("group_by")

        if x_field and y_field:
            agg_type = next(
                (a["type"] for a in aggregations if a["field"] == y_field), "sum"
            )

            if group_by:
                # Multi-level aggregation with grouping
                query["aggs"]["x_axis"] = {
                    "terms": {"field": x_field, "size": 100},
                    "aggs": {
                        "group_by": {
                            "terms": {"field": group_by, "size": 20},
                            "aggs": {"value": {agg_type: {"field": y_field}}},
                        }
                    },
                }
            else:
                # Simple x-axis aggregation
                query["aggs"]["x_axis"] = {
                    "terms": {"field": x_field, "size": 100},
                    "aggs": {"value": {agg_type: {"field": y_field}}},
                }

    elif chart_type == ChartType.LINE:
        # For line charts, use date_histogram on x_axis if it's a date
        x_field = fields.get("x_axis")
        y_field = fields.get("y_axis")
        group_by = fields.get("group_by")

        if x_field and y_field:
            agg_type = next(
                (a["type"] for a in aggregations if a["field"] == y_field), "sum"
            )

            # Use date_histogram for x-axis if time_granularity is provided
            if time_granularity:
                x_agg = {
                    "date_histogram": {
                        "field": x_field,
                        "calendar_interval": time_granularity,
                    }
                }
            else:
                # Fall back to terms aggregation if not a date field or no granularity
                x_agg = {"terms": {"field": x_field, "size": 100}}

            if group_by:
                # First group by the group_by field, then by x_axis
                query["aggs"]["group_by"] = {
                    "terms": {"field": group_by, "size": 20},
                    "aggs": {
                        "x_axis": {
                            **x_agg,
                            "aggs": {"value": {agg_type: {"field": y_field}}},
                        }
                    },
                }
            else:
                # Just aggregate by x_axis
                query["aggs"]["x_axis"] = {
                    **x_agg,
                    "aggs": {"value": {agg_type: {"field": y_field}}},
                }

    elif chart_type == ChartType.PIE:
        # For pie charts, aggregate by category
        value_field = fields.get("value")
        category_field = fields.get("category")

        if value_field and category_field:
            agg_type = next(
                (a["type"] for a in aggregations if a["field"] == value_field), "sum"
            )

            query["aggs"]["categories"] = {
                "terms": {"field": category_field, "size": 100},
                "aggs": {"value": {agg_type: {"field": value_field}}},
            }

    elif chart_type == ChartType.NUMBER:
        # For number widgets, just calculate the metric
        value_field = fields.get("value")

        if value_field:
            agg_type = next(
                (a["type"] for a in aggregations if a["field"] == value_field), "sum"
            )
            query["aggs"]["value"] = {agg_type: {"field": value_field}}

    elif chart_type == ChartType.STACKED_BAR:
        # For stacked bar charts, we need x_axis, y_axis, and stack_by fields
        x_field = fields.get("x_axis")
        y_field = fields.get("y_axis")
        stack_by = fields.get("stack_by")

        if x_field and y_field and stack_by:
            agg_type = next(
                (a["type"] for a in aggregations if a["field"] == y_field), "sum"
            )

            # First aggregate by x_axis, then by stack_by
            query["aggs"]["x_axis"] = {
                "terms": {"field": x_field, "size": 100},
                "aggs": {
                    "stack_by": {
                        "terms": {"field": stack_by, "size": 20},
                        "aggs": {"value": {agg_type: {"field": y_field}}},
                    }
                },
            }

    return query


def transform_aggregations(
    aggregations: List[AdvancedAggregation],
) -> List[Dict[str, Any]]:
    """Transform AdvancedAggregation objects to simple dict format for the query builder"""
    return [
        {"field": agg.field, "type": agg.type, "parameters": agg.parameters or {}}
        for agg in aggregations
    ]
