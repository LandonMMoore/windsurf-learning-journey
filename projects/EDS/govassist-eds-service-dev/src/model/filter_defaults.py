from typing import Dict, List

from .filter_definitions import FilterOperator, FilterType

# Default operator mappings for each field type
DEFAULT_OPERATORS: Dict[FilterType, List[FilterOperator]] = {
    FilterType.STRING: [
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH,
        FilterOperator.IS_EMPTY,
        FilterOperator.IS_NOT_EMPTY,
    ],
    FilterType.NUMBER: [
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_EQUALS,
        FilterOperator.LESS_THAN_EQUALS,
        FilterOperator.BETWEEN,
        FilterOperator.IS_EMPTY,
        FilterOperator.IS_NOT_EMPTY,
    ],
    FilterType.DATE: [
        FilterOperator.EQUALS,
        FilterOperator.BEFORE,
        FilterOperator.AFTER,
        FilterOperator.BETWEEN,
        FilterOperator.IS_EMPTY,
        FilterOperator.IS_NOT_EMPTY,
    ],
    FilterType.ENUM: [
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.IS_EMPTY,
        FilterOperator.IS_NOT_EMPTY,
    ],
    FilterType.BOOLEAN: [
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
    ],
}
