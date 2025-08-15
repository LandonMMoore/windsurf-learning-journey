from enum import Enum
from typing import Any, List, Optional

from sqlalchemy import asc, desc
from sqlalchemy.orm import Query, selectinload
from sqlalchemy.sql.expression import and_, or_

from src.consts.sortDirection import SortDirection
from src.core.config import configs
from src.core.exceptions import ValidationError
from src.util.get_field import get_field

SQLALCHEMY_QUERY_MAPPER = {
    "eq": "__eq__",
    "ne": "__ne__",
    "lt": "__lt__",
    "lte": "__le__",
    "gt": "__gt__",
    "gte": "__ge__",
}


def dict_to_sqlalchemy_filter_options(model_class, search_option_dict):
    sql_alchemy_filter_options = []
    copied_dict = search_option_dict.copy()
    for key in search_option_dict:
        attr = getattr(model_class, key, None)
        if attr is None:
            continue
        option_from_dict = copied_dict.pop(key)
        if type(option_from_dict) in [int, float]:
            sql_alchemy_filter_options.append(attr == option_from_dict)
        elif type(option_from_dict) in [str]:
            sql_alchemy_filter_options.append(attr.like("%" + option_from_dict + "%"))
        elif type(option_from_dict) in [bool]:
            sql_alchemy_filter_options.append(attr == option_from_dict)
        elif isinstance(option_from_dict, Enum):
            sql_alchemy_filter_options.append(attr == option_from_dict.value)

    for custom_option in copied_dict:
        if "__" not in custom_option:
            continue
        key, command = custom_option.split("__")
        attr = getattr(model_class, key, None)
        if attr is None:
            continue
        option_from_dict = copied_dict[custom_option]
        if command == "in":
            sql_alchemy_filter_options.append(
                attr.in_([option.strip() for option in option_from_dict.split(",")])
            )
        elif command in SQLALCHEMY_QUERY_MAPPER.keys():
            sql_alchemy_filter_options.append(
                getattr(attr, SQLALCHEMY_QUERY_MAPPER[command])(option_from_dict)
            )
        elif command == "isnull":
            bool_command = "__eq__" if option_from_dict else "__ne__"
            sql_alchemy_filter_options.append(getattr(attr, bool_command)(None))

    return and_(True, *sql_alchemy_filter_options)


def get_column_for_field(model: Any, field_name: str):
    """Get column for a nested field without modifying the query"""
    if "." not in field_name:
        return getattr(model, field_name)

    path_parts = field_name.split(".")
    current_model = model

    for part in path_parts[:-1]:
        relationship_attr = getattr(current_model, part)
        current_model = relationship_attr.property.mapper.class_

    return getattr(current_model, path_parts[-1])


def build_sort_orders(model: Any, sort_fields: List[str], query: Query) -> Any:
    orders = []
    # Track which joins have already been added to prevent duplicates
    existing_joins = set()

    for field_expr in sort_fields:
        if field_expr.startswith("-"):
            direction = SortDirection.DESC
            field = field_expr[1:]
        else:
            direction = SortDirection.ASC
            field = field_expr

        # Handle nested fields
        if "." in field:
            # Check if this join path has already been processed
            if field not in existing_joins:
                query, column = get_field(model, field, query)
                existing_joins.add(field)
            else:
                # If join already exists, just get the column without modifying query
                column = get_column_for_field(field)
        else:
            if hasattr(model, field):
                column = getattr(model, field)
            else:
                raise ValidationError(
                    detail=f"Field '{field}' does not exist on model {model.__name__}"
                )

        orders.append(desc(column) if direction == SortDirection.DESC else asc(column))

    return query, orders


def apply_eager_loading(
    query: Query, model: Any, exclude_eagers: Optional[List[str]] = None
) -> Query:
    """Apply eager loading to the query"""

    eagers = getattr(model, "eagers", [])
    if exclude_eagers:
        eagers = [eager for eager in eagers if eager not in exclude_eagers]

    for relation_path in eagers:
        path_parts = relation_path.split(".")
        current_class = model
        current_attr = getattr(current_class, path_parts[0])
        loader = selectinload(current_attr)

        for part in path_parts[1:]:
            current_class = current_attr.property.mapper.class_
            current_attr = getattr(current_class, part)
            loader = loader.selectinload(current_attr)

        query = query.options(loader)

    return query


def apply_pagination(
    query: Query, page: int = configs.PAGE, page_size: int = configs.PAGE_SIZE
) -> Query:
    """Apply pagination to the query and return results with total count"""
    total_count = query.count()

    if page_size == "all":
        results = query.all()
    else:
        page_size = int(page_size)
        results = query.limit(page_size).offset((page - 1) * page_size).all()

    return results, total_count


def apply_ordering(query: Query, model: Any, ordering: str) -> Query:
    """Apply ordering to the query"""

    if ordering:
        ordering_list = ordering.split(",")
        orders = []
        existing_joins = set()

        for field_expr in ordering_list:
            if field_expr.startswith("-"):
                direction = "desc"
                field = field_expr[1:]
            else:
                direction = "asc"
                field = field_expr

            # Handle nested fields
            if "." in field:
                if field not in existing_joins:
                    query, column = get_field(model, field, query)
                    existing_joins.add(field)
                else:
                    column = get_column_for_field(model, field)
            else:
                if hasattr(model, field):
                    column = getattr(model, field)
                else:
                    raise ValidationError(
                        detail=f"Field '{field}' does not exist on model {model.__name__}"
                    )

            orders.append(desc(column) if direction == "desc" else asc(column))

        query = query.order_by(*orders)
    else:
        query = query.order_by(model.id.desc())

    return query


def apply_search(
    query: Query,
    model: Any,
    searchable_fields: Optional[List[str]],
    search_term: Optional[str],
) -> Query:
    """Apply search to the query"""
    if not searchable_fields or not search_term:
        return query

    search_filters = []
    # Track which joins have already been added to prevent duplicates
    existing_joins = set()

    for field in searchable_fields:
        if "." in field:
            if field not in existing_joins:
                query_with_joins, column = get_field(model, field, query)
                # Update the query with the joins if they were added
                if query_with_joins is not query:
                    query = query_with_joins
                existing_joins.add(field)
            else:
                # If join already exists, just get the column without modifying query
                column = get_column_for_field(model, field)
            search_filters.append(column.ilike(f"%{search_term}%"))
        else:
            if hasattr(model, field):
                search_filters.append(getattr(model, field).ilike(f"%{search_term}%"))

    if search_filters:
        query = query.filter(or_(*search_filters))

    return query
