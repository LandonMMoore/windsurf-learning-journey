from typing import Optional

from loguru import logger

from src.elasticsearch.aggregation_utils import (
    build_linear_chart_aggs,
    build_pie_different_nested_paths_aggs,
    build_pie_nested_group_by_aggs,
    build_pie_nested_metric_aggs,
    build_pie_non_nested_aggs,
    build_pie_same_nested_path_aggs,
    build_stacked_bar_chart_aggs,
    get_es_agg_type,
    get_pie_metric_value,
    is_field_nested_simple,
    parse_linear_chart_response,
    parse_stacked_bar_chart_response,
)
from src.elasticsearch.filter_utils import build_filtered_query
from src.elasticsearch.service import es_service as es
from src.schema.dashboard_widget_schema import WidgetType


async def build_aggregation_query(
    data: dict, dashboard_id: Optional[int] = None, filter: Optional[dict] = None
):
    # Get the index name from data_source
    index_name = getattr(data, "data_source", None)
    if not index_name:
        raise ValueError("No data source specified. Please provide 'data_source'")

    if data.widget_type == WidgetType.LINE:
        return await build_linear_chart_aggregation(
            data, index_name, dashboard_id, filter
        )
    if data.widget_type == WidgetType.BAR:
        return await build_linear_chart_aggregation(
            data, index_name, dashboard_id, filter
        )
    if data.widget_type == WidgetType.NUMBER:
        return await build_number_aggregation(data, index_name, dashboard_id, filter)
    if data.widget_type == WidgetType.PIE:
        return await build_pie_chart_aggregation(data, index_name, dashboard_id, filter)
    if data.widget_type == WidgetType.STACKED_BAR:
        return await build_stacked_bar_chart_aggregation(
            data, index_name, dashboard_id, filter
        )


async def _build_enhanced_query(
    base_filters: dict,
    data_source: str,
    dashboard_id: Optional[int] = None,
    widget_config: Optional[dict] = None,
    filter: Optional[dict] = None,
) -> dict:
    """Build enhanced query with filters"""

    if dashboard_id:
        try:
            # Import here to avoid circular imports
            from src.services.filter_integration_service import FilterIntegrationService

            # Create service
            filter_integration_service = FilterIntegrationService()

            # Build enhanced query with filters
            # Use provided widget_config or create minimal one
            if widget_config is None:
                widget_config = {"data_source": data_source}
            else:
                # Handle FetchedData object properly
                if hasattr(widget_config, "dict"):
                    # It's a Pydantic model, convert to dict
                    widget_config_dict = widget_config.dict()
                else:
                    widget_config_dict = widget_config.copy()

                # Ensure data_source is included
                widget_config_dict["data_source"] = data_source

            enhanced_query = filter_integration_service.build_enhanced_query(
                widget_config_dict, dashboard_id, base_filters, filter
            )
            return enhanced_query
        except Exception as e:
            logger.error(f"Error building enhanced query with filters: {str(e)}")

    return build_filtered_query(base_filters)


def parse_aggregation_response(response, agg_name, agg_func="value_count"):
    total_docs = response["hits"]["total"]["value"]
    buckets = response["aggregations"][agg_name]["buckets"]

    results = {}
    for bucket in buckets:
        # Replace null values with 0
        value = bucket.get("metric", {}).get("value", 0)
        if value is None:
            value = 0
        results[bucket["key"]] = {agg_func: value}

    return {
        "total_documents": total_docs,
        "aggregated_data": results,
    }


def build_same_nested_path_aggs(
    field: str, metric_field: str, es_agg_func: str, size: int
) -> dict:
    """Build aggregation for fields nested in the same path."""
    return {
        "nested_data": {
            "nested": {"path": ".".join(field.split(".")[:-1])},
            "aggs": {
                "group_by": {
                    "terms": {"field": field, "size": size},
                    "aggs": {"metric": {es_agg_func: {"field": metric_field}}},
                }
            },
        }
    }


def build_different_nested_paths_aggs(
    field: str,
    metric_field: str,
    group_by_path: str,
    metric_path: str,
    es_agg_func: str,
    size: int,
) -> dict:
    """Build aggregation for fields nested in different paths."""
    return {
        "nested_data": {
            "nested": {"path": group_by_path},
            "aggs": {
                "group_by": {
                    "terms": {"field": field, "size": size},
                    "aggs": {
                        "to_root": {
                            "reverse_nested": {},
                            "aggs": {
                                "to_metric": {
                                    "nested": {"path": metric_path},
                                    "aggs": {
                                        "metric": {es_agg_func: {"field": metric_field}}
                                    },
                                }
                            },
                        }
                    },
                }
            },
        }
    }


def build_nested_group_by_aggs(
    field: str, metric_field: str, group_by_path: str, es_agg_func: str, size: int
) -> dict:
    """Build aggregation for nested group_by field with non-nested metric."""
    return {
        "nested_data": {
            "nested": {"path": group_by_path},
            "aggs": {
                "group_by": {
                    "terms": {"field": field, "size": size},
                    "aggs": {
                        "to_root": {
                            "reverse_nested": {},
                            "aggs": {"metric": {es_agg_func: {"field": metric_field}}},
                        }
                    },
                }
            },
        }
    }


def build_nested_metric_aggs(
    field: str, metric_field: str, metric_path: str, es_agg_func: str, size: int
) -> dict:
    """Build aggregation for non-nested group_by field with nested metric."""
    return {
        "nested_data": {
            "nested": {"path": metric_path},
            "aggs": {
                "to_root": {
                    "reverse_nested": {},
                    "aggs": {
                        "group_by": {
                            "terms": {"field": field, "size": size},
                            "aggs": {
                                "to_metric": {
                                    "nested": {"path": metric_path},
                                    "aggs": {
                                        "metric": {es_agg_func: {"field": metric_field}}
                                    },
                                }
                            },
                        }
                    },
                }
            },
        }
    }


def build_non_nested_aggs(
    field: str, metric_field: str, es_agg_func: str, size: int
) -> dict:
    """Build aggregation for non-nested fields."""
    metric_agg = (
        {"metric": {es_agg_func: {"field": metric_field}}}
        if metric_field
        else {"metric": {"value_count": {"field": field}}}
    )
    return {"pie_data": {"terms": {"field": field, "size": size}, "aggs": metric_agg}}


def get_metric_value(bucket: dict, agg_type: str) -> dict:
    """Extract metric value from bucket based on aggregation type."""
    if agg_type == "stats":
        metric_data = bucket["metric"]
        return {
            "count": metric_data.get("count", 0) or 0,
            "min": metric_data.get("min", 0) or 0,
            "max": metric_data.get("max", 0) or 0,
            "avg": metric_data.get("avg", 0) or 0,
            "sum": metric_data.get("sum", 0) or 0,
        }
    else:
        value = bucket["metric"].get("value", 0)
        return {agg_type: value if value is not None else 0}


def terms_clause(x_axis_field, values):
    return {"terms": {x_axis_field: values}}


def build_nested_query(nested_path, must=None, must_not=None):
    return {
        "nested": {
            "path": nested_path,
            "query": {
                "bool": {
                    **({"must": must} if must else {}),
                    **({"must_not": must_not} if must_not else {}),
                }
            },
        }
    }


def ensure_bool_structure(query):
    if "bool" not in query["query"]:
        query["query"] = {
            "bool": {"must": [], "must_not": [], "should": [], "filter": []}
        }
    if "must" not in query["query"]["bool"]:
        query["query"]["bool"]["must"] = []
    if "must_not" not in query["query"]["bool"]:
        query["query"]["bool"]["must_not"] = []


async def build_pie_chart_aggregation(
    data: dict,
    index_name: str,
    dashboard_id: Optional[int] = None,
    filter: Optional[dict] = None,
):
    try:
        field = data.config.get("group_by")
        metric_field = data.config.get("metric")
        agg_func = data.config.get("aggregate", "value_count")
        filters = data.config.get("filters", {})
        # By default the size for the aggregation is 1000. If there are any filters, the size will be automatically reduced to the number of values.
        size = 1000
        excluded_values, included_values = data.config.get(
            "excluded_values", []
        ), data.config.get("included_values", [])

        # Before we were using the values from the x_axis_config, but for the backward compatibility 
        values = data.config.get("show", [])
        if not excluded_values and not included_values and values:
            included_values = values

        # Map aggregation types to Elasticsearch-compatible type
        es_agg_func = get_es_agg_type(agg_func)

        # Build enhanced query with global filters and widget config
        query = await _build_enhanced_query(
            filters, index_name, dashboard_id, data, filter
        )

        # Check if fields are nested using the updated function
        is_group_by_nested, group_by_path = is_field_nested_simple(field)
        is_metric_nested, metric_path = (
            is_field_nested_simple(metric_field) if metric_field else (False, None)
        )

        # Add terms filter for group_by values if provided (handle nested fields)
        # BUT only if there are no dashboard filters (dashboard filters take precedence)
        if included_values or excluded_values:
            ensure_bool_structure(query)

            if is_group_by_nested and group_by_path:
                must = [terms_clause(field, included_values)] if included_values else []
                must_not = (
                    [terms_clause(field, excluded_values)] if excluded_values else []
                )

                nested_filter = build_nested_query(
                    group_by_path, must=must, must_not=must_not
                )
                query["query"]["bool"]["must"].append(nested_filter)

            else:
                if included_values:
                    query["query"]["bool"]["must"].append(
                        terms_clause(field, included_values)
                    )
                if excluded_values:
                    query["query"]["bool"]["must_not"].append(
                        terms_clause(field, excluded_values)
                    )

        # Build aggregations based on nested status
        if is_group_by_nested and is_metric_nested:
            if group_by_path == metric_path:
                query["aggs"] = build_pie_same_nested_path_aggs(
                    field, metric_field, es_agg_func, size
                )
            else:
                query["aggs"] = build_pie_different_nested_paths_aggs(
                    field, metric_field, group_by_path, metric_path, es_agg_func, size
                )
        elif is_group_by_nested:
            query["aggs"] = build_pie_nested_group_by_aggs(
                field, metric_field, group_by_path, es_agg_func, size
            )
        elif is_metric_nested:
            query["aggs"] = build_pie_nested_metric_aggs(
                field, metric_field, metric_path, es_agg_func, size
            )
        else:
            # Both fields are non-nested (could be object fields or regular fields)
            query["aggs"] = build_pie_non_nested_aggs(
                field, metric_field, es_agg_func, size
            )
        response = await es.search(index_name=index_name, query=query)

        # Get buckets based on aggregation type
        if is_group_by_nested or is_metric_nested:
            if is_metric_nested and not is_group_by_nested:
                buckets = response["aggregations"]["nested_data"]["to_root"][
                    "group_by"
                ]["buckets"]
            else:
                buckets = response["aggregations"]["nested_data"]["group_by"]["buckets"]
        else:
            buckets = response["aggregations"]["pie_data"]["buckets"]

        # Process buckets and build results
        results = {}
        for bucket in buckets:
            if is_group_by_nested and is_metric_nested:
                if group_by_path == metric_path:
                    metric_bucket = bucket
                else:
                    metric_bucket = bucket["to_root"]["to_metric"]
            elif is_group_by_nested:
                metric_bucket = bucket["to_root"]
            elif is_metric_nested:
                metric_bucket = bucket["to_metric"]
            else:
                metric_bucket = bucket

            results[bucket["key"]] = get_pie_metric_value(metric_bucket, agg_func)

        return {
            "widget_data": data,
            "data": {
                "total_documents": response["hits"]["total"]["value"],
                "aggregated_data": results,
            },
        }

    except Exception as e:
        logger.error(f"Error in build_pie_chart_aggregation: {str(e)}")
        return {"widget_data": data, "data": None}


async def build_number_aggregation(
    data: dict,
    index_name: str,
    dashboard_id: Optional[int] = None,
    filter: Optional[dict] = None,
):
    try:
        metric_field = data.config.get("metric")
        agg_func = data.config.get("aggregate", "value_count")
        filters = data.config.get("filters", {})

        # Build enhanced query with global filters and widget config
        query = await _build_enhanced_query(
            filters, index_name, dashboard_id, data, filter
        )

        if metric_field:
            is_nested = "." in metric_field
            nested_path = ".".join(metric_field.split(".")[:-1]) if is_nested else None
        else:
            is_nested, nested_path = False, None

        # Map aggregation types to Elasticsearch-compatible type
        es_agg_func = get_es_agg_type(agg_func)

        field_name = data.config.get("metric")

        is_nested, nested_path = (
            is_field_nested_simple(field_name) if field_name else (False, None)
        )

        if is_nested and nested_path:
            # Build nested aggregation for numeric/float fields
            query["aggs"] = {
                "nested_data": {
                    "nested": {"path": nested_path},
                    "aggs": {
                        "metric_agg": (
                            {es_agg_func: {"field": metric_field}}
                            if es_agg_func != "value_count"
                            else {"value_count": {"field": metric_field}}
                        )
                    },
                }
            }
        else:
            if es_agg_func == "value_count":
                if metric_field:
                    query["aggs"] = {
                        "metric_agg": {"value_count": {"field": metric_field}}
                    }
                else:
                    # If no metric field, count all documents
                    query["aggs"] = {"metric_agg": {"value_count": {"field": "_id"}}}
            else:
                query["aggs"] = {"metric_agg": {es_agg_func: {"field": metric_field}}}

        response = await es.search(index_name=index_name, query=query)

        # Extract aggregation result
        if is_nested:
            agg_result = response["aggregations"]["nested_data"]["metric_agg"]
        else:
            agg_result = response["aggregations"]["metric_agg"]

        if agg_func == "stats":
            parsed_response = {
                "total_documents": response["hits"]["total"]["value"],
                "aggregated_data": {
                    "count": agg_result.get("count", 0) or 0,
                    "min": agg_result.get("min", 0) or 0,
                    "max": agg_result.get("max", 0) or 0,
                    "avg": agg_result.get("avg", 0) or 0,
                    "sum": agg_result.get("sum", 0) or 0,
                },
            }
        else:
            value = agg_result.get("value", 0)
            if value is None:
                value = 0
            parsed_response = {
                "total_documents": response["hits"]["total"]["value"],
                "aggregated_data": {"value": value},
            }

        return {"widget_data": data, "data": parsed_response}
    except Exception as e:
        logger.error(f"Error in build_number_aggregation: {str(e)}")
        return {"widget_data": data, "data": None}


async def build_linear_chart_aggregation(
    data: dict,
    index_name: str,
    dashboard_id: Optional[int] = None,
    filter: Optional[dict] = None,
):
    try:
        x_axis_config = data.config.get("x_axis", {})
        y_axis_config = data.config.get("y_axis", {})
        filters = data.config.get("filters", {})

        # Get metrics configuration
        y_metrics = y_axis_config.get("metrics", [])
        if not y_metrics:
            y_metrics = [
                {
                    "field": x_axis_config["field"],
                    "aggregate": "value_count",
                    "name": "count",
                }
            ]

        # Build enhanced query with global filters and widget config
        query = await _build_enhanced_query(
            filters, index_name, dashboard_id, data, filter
        )

        # Add terms filter for x_axis values if provided (handle nested fields)
        # BUT only if there are no dashboard filters (dashboard filters take precedence)
        x_axis_field = x_axis_config.get("field")
        excluded_values, included_values = x_axis_config.get(
            "excluded_values", []
        ), x_axis_config.get("included_values", [])

        # Before we were using the values from the x_axis_config, but for the backward compatibility 
        values = x_axis_config.get("values", [])
        if not excluded_values and not included_values and values:
            included_values = values

        if excluded_values or included_values:
            is_nested, nested_path = is_field_nested_simple(x_axis_field)

            # Ensure bool query structure
            ensure_bool_structure(query)

            if is_nested and nested_path:
                must = (
                    [terms_clause(x_axis_field, included_values)]
                    if included_values
                    else []
                )
                must_not = (
                    [terms_clause(x_axis_field, excluded_values)]
                    if excluded_values
                    else []
                )
                query["query"]["bool"]["must"].append(
                    build_nested_query(nested_path, must=must, must_not=must_not)
                )
            else:
                if included_values:
                    query["query"]["bool"]["must"].append(
                        terms_clause(x_axis_field, included_values)
                    )
                if excluded_values:
                    query["query"]["bool"]["must_not"].append(
                        terms_clause(x_axis_field, excluded_values)
                    )
        query["aggs"] = build_linear_chart_aggs(
            x_axis_config,
            y_metrics,
            x_axis_config.get("time_range"),
            None,
        )

        response = await es.search(index_name=index_name, query=query)

        # Parse response using utility function
        chart_data = parse_linear_chart_response(response, x_axis_config, y_metrics)

        return {
            "widget_data": data,
            "data": {
                "total_documents": response["hits"]["total"]["value"],
                "chart_data": chart_data,
                "config": {
                    "x_axis": x_axis_config,
                    "y_axis": y_axis_config,
                },
            },
        }

    except Exception as e:
        logger.error(f"Error in build_linear_chart_aggregation: {str(e)}")
        return {"widget_data": data, "data": None}


async def build_stacked_bar_chart_aggregation(
    data: dict,
    index_name: str,
    dashboard_id: Optional[int] = None,
    filter: Optional[dict] = None,
):
    try:
        x_axis_config = data.config.get("x_axis", {})
        y_axis_config = data.config.get("y_axis", {})
        stack_by_config = data.config.get("stack_by", {})
        filters = data.config.get("filters", {})

        # Get metrics configuration
        y_metrics = y_axis_config.get("metrics", [])
        if not y_metrics:
            y_metrics = [
                {
                    "field": x_axis_config["field"],
                    "aggregate": "value_count",
                    "name": "count",
                }
            ]

        # Build enhanced query with global filters and widget config
        query = await _build_enhanced_query(
            filters, index_name, dashboard_id, data, filter
        )

        x_axis_field = x_axis_config.get("field")
        excluded_values, included_values = x_axis_config.get(
            "excluded_values", []
        ), x_axis_config.get("included_values", [])

        if excluded_values or included_values:
            is_nested, nested_path = is_field_nested_simple(x_axis_field)

            ensure_bool_structure(query)

            if is_nested and nested_path:
                must = (
                    [terms_clause(x_axis_field, included_values)]
                    if included_values
                    else []
                )
                must_not = (
                    [terms_clause(x_axis_field, excluded_values)]
                    if excluded_values
                    else []
                )
                query["query"] = build_nested_query(
                    nested_path, must=must, must_not=must_not
                )
            else:
                if included_values:
                    query["query"]["bool"]["must"].append(
                        terms_clause(x_axis_field, included_values)
                    )
                if excluded_values:
                    query["query"]["bool"]["must_not"].append(
                        terms_clause(x_axis_field, excluded_values)
                    )

        # Build aggregations using utility function
        query["aggs"] = build_stacked_bar_chart_aggs(
            x_axis_config,
            stack_by_config,
            y_metrics,
            x_axis_config.get("time_range"),
            None,
        )

        # Execute query
        response = await es.search(index_name=index_name, query=query)

        # Parse response using utility function
        chart_data = parse_stacked_bar_chart_response(
            response, x_axis_config, stack_by_config, y_metrics
        )

        return {
            "widget_data": data,
            "data": {
                "total_documents": response["hits"]["total"]["value"],
                "chart_data": chart_data,
                "config": {
                    "x_axis": x_axis_config,
                    "stack_by": stack_by_config,
                    "y_axis": y_axis_config,
                },
            },
        }

    except Exception as e:
        logger.error(f"Error in build_stacked_bar_chart_aggregation: {str(e)}")
        return {"widget_data": data, "data": None}
