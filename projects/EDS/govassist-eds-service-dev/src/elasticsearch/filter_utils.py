from typing import Any, Dict, List, Optional, Union


def build_bool_query() -> Dict:
    """Create a base bool query structure."""
    return {"bool": {"must": [], "must_not": [], "should": [], "filter": []}}


def build_term_query(condition: Dict) -> Optional[Dict]:
    """Build a term query based on the condition."""
    if not isinstance(condition, dict) or "field" not in condition:
        return None

    field = condition["field"]
    value = condition.get("value")
    operator = condition.get("operator", "equals").lower()
    start = condition.get("start")
    end = condition.get("end")

    # Handle None values - but allow range operations with start/end
    if (
        value is None
        and start is None
        and end is None
        and operator
        not in ["exists", "not_exists", "is_empty", "is_not_empty", "between", "range"]
    ):
        return None

    operators = {
        "equals": lambda: (
            {"terms": {field: value}}
            if isinstance(value, list)
            else {"term": {field: value}}
        ),
        "not_equals": lambda: (
            {"bool": {"must_not": [{"terms": {field: value}}]}}
            if isinstance(value, list)
            else {"bool": {"must_not": [{"term": {field: value}}]}}
        ),
        "in": lambda: (
            {"terms": {field: value}}
            if isinstance(value, list)
            else {"term": {field: value}}
        ),
        "not_in": lambda: (
            {"bool": {"must_not": [{"terms": {field: value}}]}}
            if isinstance(value, list)
            else {"bool": {"must_not": [{"term": {field: value}}]}}
        ),
        "contains": lambda: {"wildcard": {field: f"*{value}*"}} if value else None,
        "not_contains": lambda: (
            {"bool": {"must_not": [{"wildcard": {field: f"*{value}*"}}]}}
            if value
            else None
        ),
        "starts_with": lambda: {"prefix": {field: value}} if value else None,
        "ends_with": lambda: {"wildcard": {field: f"*{value}"}} if value else None,
        "greater_than": lambda: (
            {"range": {field: {"gt": value}}} if value is not None else None
        ),
        "greater_than_equals": lambda: (
            {"range": {field: {"gte": value}}} if value is not None else None
        ),
        "less_than": lambda: (
            {"range": {field: {"lt": value}}} if value is not None else None
        ),
        "less_than_equals": lambda: (
            {"range": {field: {"lte": value}}} if value is not None else None
        ),
        "between": lambda: build_range_query(
            field, condition.get("start"), condition.get("end")
        ),
        "range": lambda: build_range_query(
            field, condition.get("start"), condition.get("end")
        ),
        "exists": lambda: {"exists": {"field": field}},
        "not_exists": lambda: {
            "bool": {
                "must_not": [
                    (
                        {"exists": {"field": field}}
                        if value is None
                        else (
                            {"terms": {field: value}}
                            if isinstance(value, list)
                            else {"term": {field: value}}
                        )
                    )
                ]
            }
        },
        "is_empty": lambda: {"bool": {"must_not": [{"exists": {"field": field}}]}},
        "is_not_empty": lambda: {"exists": {"field": field}},
    }

    query = operators.get(operator, operators["equals"])()
    return (
        query
        if query is not None
        else {"term": {field: value}} if value is not None else None
    )


def build_range_query(field: str, start: Any = None, end: Any = None) -> Optional[Dict]:
    """Build a range query for date or numeric fields."""
    if start is None and end is None:
        return None

    range_query = {"range": {field: {}}}
    if start is not None:
        range_query["range"][field]["gte"] = start
    if end is not None:
        range_query["range"][field]["lte"] = end
    return range_query


VALID_OPERATORS = {"and", "or"}


def process_enhanced_filter_condition(filter_condition: Dict) -> Optional[Dict]:
    if not isinstance(filter_condition, dict):
        return None

    # Check if this is a logical group (has operator and conditions)
    if "operator" in filter_condition and "conditions" in filter_condition:
        operator = filter_condition["operator"].lower()
        conditions = filter_condition.get("conditions", [])

        if operator not in VALID_OPERATORS or not isinstance(conditions, list):
            return None

        if not conditions:
            return None

        # Process all conditions recursively
        processed_conditions = []
        for condition in conditions:
            processed = process_enhanced_filter_condition(condition)
            if processed:
                processed_conditions.append(processed)

        if not processed_conditions:
            return None

        # Build the appropriate bool query based on operator
        if operator == "and":
            return {"bool": {"must": processed_conditions}}
        elif operator == "or":
            return {"bool": {"should": processed_conditions, "minimum_should_match": 1}}

    # Check if this is a field condition (has field name as key with operator/value)
    elif len(filter_condition) == 1:
        field_name = list(filter_condition.keys())[0]
        field_config = filter_condition[field_name]

        if not field_name or not isinstance(field_config, dict):
            return None

        if "operator" not in field_config:
            return None

        # Build the field condition
        condition = {
            "field": field_name,
            "operator": field_config["operator"],
            "value": field_config.get("value"),
        }

        # Add start/end for range operations
        if "start" in field_config:
            condition["start"] = field_config["start"]
        if "end" in field_config:
            condition["end"] = field_config["end"]

        return build_term_query(condition)

    return None


def add_filter_condition(
    query: Dict, filter_condition: Dict, bool_type: str = "must"
) -> None:
    """Add a filter condition to the query."""
    if not isinstance(filter_condition, dict):
        return

    # Check if this is a complex filter with operator and conditions (AND/OR/NOT logic)
    if "operator" in filter_condition and "conditions" in filter_condition:
        operator = filter_condition["operator"].lower()
        conditions = filter_condition.get("conditions", [])

        if not conditions:
            return

        if operator == "and":
            # For AND conditions, add each condition directly to the must array
            for condition in conditions:
                if isinstance(condition, dict) and "field" in condition:
                    term_query = build_term_query(condition)
                    if term_query:
                        query["query"]["bool"][bool_type].append(term_query)
        elif operator == "or":
            # Create a new bool query for OR conditions
            or_query = {"bool": {"should": [], "minimum_should_match": 1}}
            for condition in conditions:
                if isinstance(condition, dict) and "field" in condition:
                    term_query = build_term_query(condition)
                    if term_query:
                        or_query["bool"]["should"].append(term_query)
            if or_query["bool"]["should"]:
                query["query"]["bool"][bool_type].append(or_query)

    # Check if this is a single field filter with operator (like greater_than, less_than, etc.)
    elif "field" in filter_condition and "operator" in filter_condition:
        term_query = build_term_query(filter_condition)
        if term_query:
            query["query"]["bool"][bool_type].append(term_query)

    # Check if this is a simple field filter (just has field name)
    elif "field" in filter_condition:
        term_query = build_term_query(filter_condition)
        if term_query:
            query["query"]["bool"][bool_type].append(term_query)


def process_filters(query: Dict, filters: Optional[Union[Dict, List]] = None) -> None:
    """Process filters and add them to the query."""
    if not filters:
        return

    if isinstance(filters, dict):
        # Check if this is an enhanced filter structure
        if "operator" in filters and "conditions" in filters:
            # Process enhanced filter structure
            processed_filter = process_enhanced_filter_condition(filters)
            if processed_filter:
                # Add the processed filter to the query
                if "bool" in processed_filter:
                    # If it's a bool query, merge it with the existing bool query
                    bool_query = processed_filter["bool"]
                    for bool_type in ["must", "must_not", "should", "filter"]:
                        if bool_type in bool_query and bool_query[bool_type]:
                            query["query"]["bool"][bool_type].extend(
                                bool_query[bool_type]
                            )
                else:
                    # If it's a simple query, add it to must
                    query["query"]["bool"]["must"].append(processed_filter)
        # If the filter has an operator, it's a complex filter (legacy format)
        elif "operator" in filters:
            add_filter_condition(query, filters)
        else:
            # Handle simple filters
            for filter_field, filter_value in filters.items():
                if filter_value is None:
                    continue

                if isinstance(filter_value, dict):
                    # Handle complex filter conditions
                    if "operator" in filter_value:
                        # Add the field name to the filter condition
                        filter_condition = filter_value.copy()
                        filter_condition["field"] = filter_field
                        add_filter_condition(query, filter_condition)
                    else:
                        # Handle other complex filter conditions
                        add_filter_condition(query, filter_value)
                else:
                    # Handle simple key-value filters
                    if isinstance(filter_value, list):
                        if filter_value:  # Only add if list is not empty
                            query["query"]["bool"]["must"].append(
                                {"terms": {filter_field: filter_value}}
                            )
                    else:
                        query["query"]["bool"]["must"].append(
                            {"term": {filter_field: filter_value}}
                        )
    elif isinstance(filters, list):
        # Handle array of filter conditions
        for filter_condition in filters:
            if filter_condition:  # Skip None or empty conditions
                add_filter_condition(query, filter_condition)


def build_filtered_query(filters: Optional[Union[Dict, List]] = None) -> Dict:
    """Build a complete query with filters."""
    query = {"size": 0, "query": build_bool_query()}

    if filters:
        process_filters(query, filters)

    # Clean up empty bool query
    bool_query = query["query"]["bool"]
    if not any(
        [
            bool_query["must"],
            bool_query["must_not"],
            bool_query["should"],
            bool_query["filter"],
        ]
    ):
        query["query"] = {"match_all": {}}
    elif (
        len(bool_query["must"]) == 1
        and not bool_query["must_not"]
        and not bool_query["should"]
        and not bool_query["filter"]
    ):
        # If there's only one must condition, simplify the query
        query["query"] = bool_query["must"][0]

    return query
