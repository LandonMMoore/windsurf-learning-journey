from typing import Any, Dict, Union

from src.elasticsearch.constants import AggregationType

NESTED_PATHS = {}

OBJECT_PATHS = {}


def is_field_nested_simple(field_name: str) -> tuple[bool, str]:
    """
    Simple function to detect if a field is nested based on known nested paths.
    This is a simpler approach than checking Elasticsearch mapping.
    """
    if "." not in field_name:
        return False, None

    # Check if any part of the field path matches a known nested path
    field_parts = field_name.split(".")
    for i in range(len(field_parts) - 1, 0, -1):
        candidate_path = ".".join(field_parts[:i])
        if candidate_path in NESTED_PATHS:
            return True, candidate_path
        elif candidate_path in OBJECT_PATHS:
            # Object fields are not nested, but they have dot notation
            return False, None

    return False, None


def build_pie_same_nested_path_aggs(
    field: str, metric_field: str, es_agg_func: str, size: int
) -> Dict[str, Any]:
    """Build pie chart aggregation for fields nested in the same path."""
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


def build_pie_different_nested_paths_aggs(
    field: str,
    metric_field: str,
    group_by_path: str,
    metric_path: str,
    es_agg_func: str,
    size: int,
) -> Dict[str, Any]:
    """Build pie chart aggregation for fields nested in different paths."""
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


def build_pie_nested_group_by_aggs(
    field: str, metric_field: str, group_by_path: str, es_agg_func: str, size: int
) -> Dict[str, Any]:
    """Build pie chart aggregation for nested group_by field with non-nested metric."""
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


def build_pie_nested_metric_aggs(
    field: str, metric_field: str, metric_path: str, es_agg_func: str, size: int
) -> Dict[str, Any]:
    """Build pie chart aggregation for non-nested group_by field with nested metric."""
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


def build_pie_non_nested_aggs(
    field: str, metric_field: str, es_agg_func: str, size: int
) -> Dict[str, Any]:
    """Build pie chart aggregation for non-nested fields."""
    metric_agg = (
        {"metric": {es_agg_func: {"field": metric_field}}}
        if metric_field
        else {"metric": {"value_count": {"field": field}}}
    )
    return {"pie_data": {"terms": {"field": field, "size": size}, "aggs": metric_agg}}


def get_pie_metric_value(bucket: dict, agg_type: str) -> Dict[str, Any]:
    """Extract metric value from bucket based on aggregation type for pie charts."""
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


def build_number_nested_aggregation(
    field_path: str, metric_field: str, agg_type: str
) -> Dict[str, Any]:
    """
    Build a nested aggregation query for Elasticsearch.

    Args:
        field_path: The path to the nested field (e.g., 'budget_info.budget_items')
        metric_field: The field to aggregate on (e.g., 'lifetime_budget')
        agg_type: The type of aggregation to perform (e.g., 'sum', 'avg')

    Returns:
        Dict containing the nested aggregation query
    """
    # Split the path into parts
    path_parts = field_path.split(".")

    # Start with the innermost aggregation
    current_agg = {"metric": {agg_type: {"field": f"{field_path}.{metric_field}"}}}

    # Build the nested structure from inside out
    for path in reversed(path_parts):
        current_agg = {
            path: {
                "nested": {"path": ".".join(path_parts[: path_parts.index(path) + 1])},
                "aggs": current_agg,
            }
        }

    return current_agg


def parse_nested_aggregation_response(
    response: Dict[str, Any], field_path: str, agg_func: str
) -> Union[float, int]:
    """
    Parse the response from a nested aggregation query.

    Args:
        response: The Elasticsearch response
        field_path: The path to the nested field
        agg_func: The aggregation function used

    Returns:
        The aggregated value
    """
    # Split the path into parts
    path_parts = field_path.split(".")

    # Navigate through the response to get to the metric value
    current = response["aggregations"]
    for part in path_parts:
        if part in current:
            current = current[part]

    # Get the final metric value
    value = current.get("metric", {}).get("value", 0)
    return value if value is not None else 0


def get_es_agg_type(agg_type: str) -> str:
    """Map our aggregation types to Elasticsearch-compatible types"""
    agg_type_mapping = {
        AggregationType.COUNT: "value_count",
        AggregationType.DISTINCT_COUNT: "cardinality",
        AggregationType.SUM: "sum",
        AggregationType.AVG: "avg",
        AggregationType.MIN: "min",
        AggregationType.MAX: "max",
    }
    return agg_type_mapping.get(agg_type, agg_type)


def build_linear_date_histogram_aggs(
    field: str,
    interval: str,
    format: str,
    min_doc_count: int = 0,
    extended_bounds: dict = None,
) -> Dict[str, Any]:
    """Build date histogram aggregation for linear charts."""
    agg = {
        "date_histogram": {
            "field": field,
            "calendar_interval": interval,
            "format": format,
            "min_doc_count": min_doc_count,
        }
    }
    if extended_bounds:
        agg["date_histogram"]["extended_bounds"] = extended_bounds
    return agg


def build_linear_terms_aggs(
    field: str, size: int, include: list = None
) -> Dict[str, Any]:
    """Build terms aggregation for linear charts."""
    terms_agg = {"terms": {"field": field, "size": size}}
    if include:
        terms_agg["terms"]["include"] = include
    return terms_agg


def build_linear_histogram_aggs(field: str, interval: float) -> Dict[str, Any]:
    """Build histogram aggregation for linear charts."""
    return {"histogram": {"field": field, "interval": interval}}


def build_linear_nested_x_axis_aggs(
    x_field: str,
    x_type: str,
    x_path: str,
    interval: str = None,
    format: str = None,
    size: int = None,
    extended_bounds: dict = None,
    include: list = None,
) -> Dict[str, Any]:
    """Build nested x-axis aggregation for linear charts."""
    inner_agg = {}
    if x_type == "date":
        inner_agg = build_linear_date_histogram_aggs(
            x_field, interval, format, 0, extended_bounds
        )
    elif x_type in ["terms", "text", "keyword"]:  # Handle text fields as terms
        inner_agg = build_linear_terms_aggs(x_field, size, include)
    elif x_type == "histogram":
        inner_agg = build_linear_histogram_aggs(x_field, interval)
    else:
        # Default to terms for unknown types
        inner_agg = build_linear_terms_aggs(x_field, size, include)

    return {"nested_x": {"nested": {"path": x_path}, "aggs": {"x_axis": inner_agg}}}


def build_linear_metric_aggs(
    metric: dict, is_nested: bool = False, nested_path: str = None
) -> Dict[str, Any]:
    """Build metric aggregation for linear charts."""
    field = metric["field"]
    agg_type = get_es_agg_type(metric["aggregate"])
    metric_name = metric.get("name", f"{field}_{metric['aggregate']}")

    if is_nested:
        return {
            metric_name: {
                "nested": {"path": nested_path},
                "aggs": {"metric": {agg_type: {"field": field}}},
            }
        }
    else:
        return {metric_name: {agg_type: {"field": field}}}


def build_linear_nested_metric_with_reverse_aggs(
    metric: dict, nested_path: str, from_nested_path: str = None
) -> Dict[str, Any]:
    """Build nested metric aggregation with reverse nested for linear charts."""
    field = metric["field"]
    agg_type = get_es_agg_type(metric["aggregate"])
    metric_name = metric.get("name", f"{field}_{metric['aggregate']}")

    if from_nested_path:
        # We're already in a nested context and need to go to another
        return {
            metric_name: {
                "reverse_nested": {},
                "aggs": {
                    "to_metric": {
                        "nested": {"path": nested_path},
                        "aggs": {"metric": {agg_type: {"field": field}}},
                    }
                },
            }
        }
    else:
        # We're at root level
        return {
            metric_name: {
                "nested": {"path": nested_path},
                "aggs": {"metric": {agg_type: {"field": field}}},
            }
        }


def build_linear_chart_aggs(
    x_config: dict, metrics: list, time_range: dict = None, include_values: list = None
) -> Dict[str, Any]:
    """
    Build complete linear chart aggregation.

    Args:
        x_config: X-axis configuration (field, type, interval, etc.)
        metrics: List of metric configurations
        time_range: Optional time range for date histograms
        include_values: Optional list of values to include in terms aggregation
    """
    x_field = x_config.get("field")
    if not x_field:
        raise ValueError("X-axis field is required")

    x_interval = x_config.get("interval", "1d")
    x_type = x_config.get("type", "date")
    x_format = x_config.get("format", "yyyy-MM-dd")
    x_size = x_config.get("size", 1000)

    # Check if fields are nested using simple detection
    is_x_nested, x_path = is_field_nested_simple(x_field)
    if not is_x_nested:
        # Fallback to manual detection if simple detection fails
        is_x_nested = "." in x_field and x_config.get("is_nested", False)
        x_path = ".".join(x_field.split(".")[:-1]) if is_x_nested else None

    # Prepare extended bounds for date histogram
    extended_bounds = None
    if time_range and x_type == "date":
        extended_bounds = {"min": time_range.get("start"), "max": time_range.get("end")}

    # Start building the aggregation
    if is_x_nested:
        aggs = build_linear_nested_x_axis_aggs(
            x_field,
            x_type,
            x_path,
            x_interval,
            x_format,
            x_size,
            extended_bounds,
            include_values,
        )
        x_aggs = aggs["nested_x"]["aggs"]["x_axis"]
    else:
        if x_type == "date":
            x_aggs = build_linear_date_histogram_aggs(
                x_field, x_interval, x_format, 0, extended_bounds
            )
        elif x_type in ["terms", "text", "keyword"]:  # Handle text fields as terms
            x_aggs = build_linear_terms_aggs(x_field, x_size, include_values)
        elif x_type == "histogram":
            x_aggs = build_linear_histogram_aggs(x_field, x_interval)
        else:
            # Default to terms for unknown types
            x_aggs = build_linear_terms_aggs(x_field, x_size, include_values)

    # Add metric aggregations
    metric_aggs = {}
    for metric in metrics:
        metric_field = metric.get("field")
        if not metric_field:
            continue  # Skip metrics without field

        # Check if metric is nested using simple detection
        is_metric_nested, metric_path = is_field_nested_simple(metric_field)
        if not is_metric_nested:
            # Fallback to manual detection if simple detection fails
            is_metric_nested = "." in metric_field and metric.get("is_nested", False)
            metric_path = (
                ".".join(metric_field.split(".")[:-1]) if is_metric_nested else None
            )

        if is_metric_nested:
            if is_x_nested:
                if metric_path == x_path:
                    # Metric is nested in same path as x-axis
                    metric_aggs.update(build_linear_metric_aggs(metric))
                else:
                    # Metric is nested in different path
                    metric_aggs.update(
                        build_linear_nested_metric_with_reverse_aggs(
                            metric, metric_path, x_path
                        )
                    )
            else:
                # Only metric is nested
                metric_aggs.update(
                    build_linear_nested_metric_with_reverse_aggs(metric, metric_path)
                )
        else:
            if is_x_nested:
                # Need to go back to root for non-nested metric
                metric_aggs.update(
                    {
                        metric.get("name", f"{metric_field}_{metric['aggregate']}"): {
                            "reverse_nested": {},
                            "aggs": {
                                "metric": {
                                    get_es_agg_type(metric["aggregate"]): {
                                        "field": metric_field
                                    }
                                }
                            },
                        }
                    }
                )
            else:
                # Neither is nested (including object fields like fhwa.soar_grant)
                metric_aggs.update(build_linear_metric_aggs(metric))

    # Combine x-axis and metrics
    if is_x_nested:
        aggs["nested_x"]["aggs"]["x_axis"]["aggs"] = metric_aggs
        return aggs
    else:
        return {"x_axis": {**x_aggs, "aggs": metric_aggs}}


def get_linear_metric_value(
    bucket: dict, metric: dict, is_nested: bool = False, from_nested: bool = False
) -> float:
    """Extract metric value from bucket for linear charts."""
    metric_name = metric.get("name", f"{metric['field']}_{metric['aggregate']}")

    if from_nested:
        # Coming from nested context to another nested context
        value = bucket[metric_name]["to_metric"]["metric"].get("value", 0)
    elif is_nested:
        # Direct nested metric
        value = bucket[metric_name]["metric"].get("value", 0)
    else:
        # Non-nested metric
        value = bucket[metric_name].get("value", 0)

    return value if value is not None else 0


def parse_linear_chart_response(
    response: Dict[str, Any], x_config: dict, metrics: list
) -> Dict[str, Any]:
    """Parse linear chart response and extract values."""
    # Check if x-axis is nested using simple detection
    is_x_nested, x_path = is_field_nested_simple(x_config["field"])
    if not is_x_nested:
        # Fallback to manual detection if simple detection fails
        is_x_nested = "." in x_config["field"] and x_config.get("is_nested", False)
        x_path = ".".join(x_config["field"].split(".")[:-1]) if is_x_nested else None

    # Get the buckets based on nesting
    try:
        if is_x_nested:
            buckets = response["aggregations"]["nested_x"]["x_axis"]["buckets"]
        else:
            buckets = response["aggregations"]["x_axis"]["buckets"]
    except (KeyError, TypeError):
        # If aggregations don't exist or are malformed, return empty result
        return {
            "x_values": [],
            "y_values": {
                metric.get("name", f"{metric['field']}_{metric['aggregate']}"): []
                for metric in metrics
            },
        }

    # Process buckets
    x_values = []
    y_values = {
        metric.get("name", f"{metric['field']}_{metric['aggregate']}"): []
        for metric in metrics
    }

    for bucket in buckets:
        # Get x value
        x_value = bucket.get("key_as_string", bucket.get("key"))
        x_values.append(x_value)

        # Get y values for each metric
        for metric in metrics:
            metric_field = metric["field"]
            # Check if metric is nested using simple detection
            is_metric_nested, metric_path = is_field_nested_simple(metric_field)
            if not is_metric_nested:
                # Fallback to manual detection if simple detection fails
                is_metric_nested = "." in metric_field and metric.get(
                    "is_nested", False
                )
                metric_path = (
                    ".".join(metric_field.split(".")[:-1]) if is_metric_nested else None
                )

            if is_metric_nested and is_x_nested:
                if metric_path == x_path:
                    # Same nested path
                    value = get_linear_metric_value(bucket, metric)
                else:
                    # Different nested path - need to handle reverse_nested and then nested
                    value = get_linear_metric_value(bucket, metric, True, True)
            elif is_metric_nested:
                # Only metric is nested
                value = get_linear_metric_value(bucket, metric, True)
            elif is_x_nested:
                # Only x is nested, metric is at root
                metric_name = metric.get(
                    "name", f"{metric_field}_{metric['aggregate']}"
                )
                value = bucket[metric_name]["metric"].get("value", 0)
            else:
                # Neither is nested (including object fields like fhwa.soar_grant)
                value = get_linear_metric_value(bucket, metric)

            if value is None:
                value = 0
            y_values[
                metric.get("name", f"{metric['field']}_{metric['aggregate']}")
            ].append(value)

    return {"x_values": x_values, "y_values": y_values}


def build_stacked_nested_x_axis_aggs(
    x_field: str,
    x_type: str,
    x_path: str,
    stack_field: str,
    stack_size: int,
    interval: str = None,
    format: str = None,
    size: int = None,
    extended_bounds: dict = None,
    include: list = None,
) -> Dict[str, Any]:
    """Build nested x-axis aggregation for stacked bar charts."""
    inner_agg = {}
    if x_type == "date":
        inner_agg = build_linear_date_histogram_aggs(
            x_field, interval, format, 0, extended_bounds
        )
    elif x_type in ["terms", "text", "keyword"]:
        inner_agg = build_linear_terms_aggs(x_field, size, include)
    elif x_type == "histogram":
        inner_agg = build_linear_histogram_aggs(x_field, interval)
    else:
        inner_agg = build_linear_terms_aggs(x_field, size, include)

    return {"nested_x": {"nested": {"path": x_path}, "aggs": {"x_axis": inner_agg}}}


def build_stacked_bar_chart_aggs(
    x_config: dict,
    stack_config: dict,
    metrics: list,
    time_range: dict = None,
    include_values: list = None,
) -> Dict[str, Any]:
    """
    Build complete stacked bar chart aggregation.

    Args:
        x_config: X-axis configuration (field, type, interval, etc.)
        stack_config: Stack by configuration (field, size)
        metrics: List of metric configurations
        time_range: Optional time range for date histograms
        include_values: Optional list of values to include in terms aggregation
    """
    x_field = x_config.get("field")
    if not x_field:
        raise ValueError("X-axis field is required")

    stack_field = stack_config.get("field")
    if not stack_field:
        raise ValueError("Stack by field is required")

    x_interval = x_config.get("interval", "1d")
    x_type = x_config.get("type", "date")
    x_format = x_config.get("format", "yyyy-MM-dd")
    x_size = x_config.get("size", 1000)
    stack_size = stack_config.get("size", 10)

    # Check if fields are nested (only if they are actually of type 'nested')
    # Object fields like fhwa, organization, cost_center, award use dot notation but are not nested
    is_x_nested = "." in x_field and x_config.get("is_nested", False)
    is_stack_nested = "." in stack_field and stack_config.get("is_nested", False)
    x_path = ".".join(x_field.split(".")[:-1]) if is_x_nested else None
    stack_path = ".".join(stack_field.split(".")[:-1]) if is_stack_nested else None

    # Prepare extended bounds for date histogram
    extended_bounds = None
    if time_range and x_type == "date":
        extended_bounds = {"min": time_range.get("start"), "max": time_range.get("end")}

    # Start building the aggregation
    if is_x_nested:
        aggs = build_stacked_nested_x_axis_aggs(
            x_field,
            x_type,
            x_path,
            stack_field,
            stack_size,
            x_interval,
            x_format,
            x_size,
            extended_bounds,
            include_values,
        )
        x_aggs = aggs["nested_x"]["aggs"]["x_axis"]
    else:
        if x_type == "date":
            x_aggs = build_linear_date_histogram_aggs(
                x_field, x_interval, x_format, 0, extended_bounds
            )
        elif x_type in ["terms", "text", "keyword"]:
            x_aggs = build_linear_terms_aggs(x_field, x_size, include_values)
        elif x_type == "histogram":
            x_aggs = build_linear_histogram_aggs(x_field, x_interval)
        else:
            x_aggs = build_linear_terms_aggs(x_field, x_size, include_values)

    # Add stack by aggregation
    if is_stack_nested:
        if is_x_nested:
            if stack_path == x_path:
                # Stack is in same path as x-axis
                x_aggs["aggs"] = {
                    "stack_by": {
                        "terms": {"field": stack_field, "size": stack_size},
                        "aggs": {},
                    }
                }
            else:
                # Stack is in different path
                x_aggs["aggs"] = {
                    "stack_by": {
                        "reverse_nested": {},
                        "aggs": {
                            "to_stack": {
                                "nested": {"path": stack_path},
                                "aggs": {
                                    "stack_terms": {
                                        "terms": {
                                            "field": stack_field,
                                            "size": stack_size,
                                        },
                                        "aggs": {},
                                    }
                                },
                            }
                        },
                    }
                }
        else:
            # Only stack is nested
            x_aggs["aggs"] = {
                "stack_by": {
                    "nested": {"path": stack_path},
                    "aggs": {
                        "stack_terms": {
                            "terms": {"field": stack_field, "size": stack_size},
                            "aggs": {},
                        }
                    },
                }
            }
    else:
        # Stack is not nested (including object fields)
        x_aggs["aggs"] = {
            "stack_by": {
                "terms": {"field": stack_field, "size": stack_size},
                "aggs": {},
            }
        }

    # Add metric aggregations
    metric_aggs = {}
    for metric in metrics:
        metric_field = metric.get("field")
        if not metric_field:
            continue  # Skip metrics without field

        # Check if metric is nested (only if it's actually of type 'nested')
        is_metric_nested = "." in metric_field and metric.get("is_nested", False)
        metric_path = (
            ".".join(metric_field.split(".")[:-1]) if is_metric_nested else None
        )

        if is_metric_nested:
            if is_stack_nested and metric_path == stack_path:
                # Metric is in same path as stack
                metric_aggs.update(build_linear_metric_aggs(metric))
            elif is_x_nested and metric_path == x_path:
                # Metric is in same path as x-axis
                if is_stack_nested:
                    # Need to go through stack path
                    metric_aggs.update(
                        build_linear_nested_metric_with_reverse_aggs(
                            metric, metric_path, stack_path
                        )
                    )
                else:
                    metric_aggs.update(build_linear_metric_aggs(metric))
            else:
                # Metric is in different path
                metric_aggs.update(
                    build_linear_nested_metric_with_reverse_aggs(
                        metric, metric_path, stack_path if is_stack_nested else None
                    )
                )
        else:
            if is_stack_nested:
                # Need to go to root for non-nested metric
                metric_aggs.update(
                    {
                        metric.get("name", f"{metric_field}_{metric['aggregate']}"): {
                            "reverse_nested": {},
                            "aggs": {
                                "metric": {
                                    get_es_agg_type(metric["aggregate"]): {
                                        "field": metric_field
                                    }
                                }
                            },
                        }
                    }
                )
            else:
                # Neither is nested (including object fields)
                metric_aggs.update(build_linear_metric_aggs(metric))

    # Add metrics to the appropriate level
    if is_x_nested:
        if is_stack_nested and stack_path == x_path:
            # Stack is in same path as x-axis
            aggs["nested_x"]["aggs"]["x_axis"]["aggs"]["stack_by"]["aggs"] = metric_aggs
        elif is_stack_nested:
            # Stack is in different path
            aggs["nested_x"]["aggs"]["x_axis"]["aggs"]["stack_by"]["aggs"]["to_stack"][
                "aggs"
            ]["stack_terms"]["aggs"] = metric_aggs
        else:
            # Stack is not nested
            aggs["nested_x"]["aggs"]["x_axis"]["aggs"]["stack_by"]["aggs"] = metric_aggs
        return aggs
    else:
        if is_stack_nested:
            # Only stack is nested
            x_aggs["aggs"]["stack_by"]["aggs"]["stack_terms"]["aggs"] = metric_aggs
        else:
            # Neither is nested
            x_aggs["aggs"]["stack_by"]["aggs"] = metric_aggs
        return {"x_axis": x_aggs}


def parse_stacked_bar_chart_response(
    response: Dict[str, Any], x_config: dict, stack_config: dict, metrics: list
) -> Dict[str, Any]:
    """Parse stacked bar chart response and extract values."""
    is_x_nested = "." in x_config["field"]
    is_stack_nested = "." in stack_config["field"]

    # Get the buckets based on nesting
    try:
        if is_x_nested:
            x_buckets = response["aggregations"]["nested_x"]["x_axis"]["buckets"]
        else:
            x_buckets = response["aggregations"]["x_axis"]["buckets"]
    except (KeyError, TypeError):
        # If aggregations don't exist or are malformed, return empty result
        return {
            "x_values": [],
            "stack_values": [],
            "series": [],
        }

    # Process buckets
    x_values = []
    stack_values = set()
    series = []

    # First pass - collect all stack values
    for x_bucket in x_buckets:
        if is_stack_nested:
            if "to_root" in x_bucket:
                if "to_stack" in x_bucket["to_root"]["aggs"]:
                    stack_buckets = x_bucket["to_root"]["to_stack"]["stack_by"][
                        "buckets"
                    ]
                else:
                    stack_buckets = x_bucket["to_root"]["stack_by"]["buckets"]
            else:
                stack_buckets = x_bucket["to_stack"]["stack_by"]["buckets"]
        else:
            if "to_root" in x_bucket:
                stack_buckets = x_bucket["to_root"]["stack_by"]["buckets"]
            else:
                stack_buckets = x_bucket["stack_by"]["buckets"]

        for stack_bucket in stack_buckets:
            stack_values.add(stack_bucket["key"])

    stack_values = sorted(list(stack_values))

    # Second pass - collect values
    for x_bucket in x_buckets:
        x_value = x_bucket.get("key_as_string", x_bucket.get("key"))
        x_values.append(x_value)

        # Create a mapping of stack value to metric value
        for metric in metrics:
            metric_name = metric.get("name", f"{metric['field']}_{metric['aggregate']}")
            stack_map = {stack_value: 0 for stack_value in stack_values}

            # Get stack buckets
            if is_stack_nested:
                if "to_root" in x_bucket:
                    if "to_stack" in x_bucket["to_root"]["aggs"]:
                        stack_buckets = x_bucket["to_root"]["to_stack"]["stack_by"][
                            "buckets"
                        ]
                    else:
                        stack_buckets = x_bucket["to_root"]["stack_by"]["buckets"]
                else:
                    stack_buckets = x_bucket["to_stack"]["stack_by"]["buckets"]
            else:
                if "to_root" in x_bucket:
                    stack_buckets = x_bucket["to_root"]["stack_by"]["buckets"]
                else:
                    stack_buckets = x_bucket["stack_by"]["buckets"]

            for stack_bucket in stack_buckets:
                stack_value = stack_bucket["key"]
                if "." in metric["field"]:  # Nested metric
                    if "to_metric" in stack_bucket[metric_name]:
                        value = stack_bucket[metric_name]["to_metric"]["metric"].get(
                            "value", 0
                        )
                    else:
                        value = stack_bucket[metric_name]["metric"].get("value", 0)
                else:
                    if "metric" in stack_bucket[metric_name]:
                        value = stack_bucket[metric_name]["metric"].get("value", 0)
                    else:
                        value = stack_bucket[metric_name].get("value", 0)

                stack_map[stack_value] = value if value is not None else 0

            series.append(
                {
                    "x": x_value,
                    "metric": metric_name,
                    "values": [stack_map[stack_value] for stack_value in stack_values],
                }
            )

    return {"x_values": x_values, "stack_values": stack_values, "series": series}
