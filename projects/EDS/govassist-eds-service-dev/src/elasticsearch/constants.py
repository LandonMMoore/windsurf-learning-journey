from enum import Enum


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    NUMBER = "number"
    STACKED_BAR = "stacked_bar"


class AggregationType(str, Enum):
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    DISTINCT_COUNT = "distinct_count"
    MONTH_OVER_MONTH = "month_over_month"
    QUARTER_OVER_QUARTER = "quarter_over_quarter"
    YEAR_OVER_YEAR = "year_over_year"


class TimeGranularity(str, Enum):
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"


class FieldType(str, Enum):
    NUMERIC = "numeric"
    TEXT = "text"
    KEYWORD = "keyword"
    DATE = "date"
    BOOLEAN = "boolean"
    NESTED = "nested"
    OBJECT = "object"
    GEO_POINT = "geo_point"
    IP = "ip"


APPROVED_PAR_CHART_FIELDS = {
    # par index fields - root level fields that still exist at root
    "account": {
        "field_name": "account.keyword",
        "display_name": "Account",
    },
    "award_number": {
        "field_name": "award_number.keyword",
        "display_name": "Award Number",
    },
    "award_status": {
        "field_name": "award_status.keyword",
        "display_name": "Award Status",
    },
    "account_name": {
        "field_name": "account_name.keyword",
        "display_name": "Account Name",
    },
    "account_parent1": {
        "field_name": "account_parent1.keyword",
        "display_name": "Account Parent 1",
    },
    "account_parent1_description": {
        "field_name": "account_parent1_description.keyword",
        "display_name": "Account Parent 1 Description",
    },
    "allotment_balance": {
        "field_name": "allotment_balance",
        "display_name": "Allotment Balance",
    },
    "award_cfda_no": {
        "field_name": "award_cfda_no.keyword",
        "display_name": "Award CFDA No",
    },
    "award_end_date": {
        "field_name": "award_end_date",
        "display_name": "Award End Date",
    },
    "award_name": {
        "field_name": "award_name.keyword",
        "display_name": "Award Name",
    },
    "award_organization": {
        "field_name": "award_organization.keyword",
        "display_name": "Award Organization",
    },
    "award_sponsor": {
        "field_name": "award_sponsor.keyword",
        "display_name": "Award Sponsor",
    },
    "award_start_date": {
        "field_name": "award_start_date",
        "display_name": "Award Start Date",
    },
    "award_type": {
        "field_name": "award_type.keyword",
        "display_name": "Award Type",
    },
    "commitment": {
        "field_name": "commitment",
        "display_name": "Commitment",
    },
    "cost_center": {
        "field_name": "cost_center.keyword",
        "display_name": "Cost Center",
    },
    "cost_center_name": {
        "field_name": "cost_center_name.keyword",
        "display_name": "Cost Center Name",
    },
    "cost_center_parent1": {
        "field_name": "cost_center_parent1.keyword",
        "display_name": "Cost Center Parent 1",
    },
    "cost_center_parent1_description": {
        "field_name": "cost_center_parent1_description.keyword",
        "display_name": "Cost Center Parent 1 Description",
    },
    "expenditures": {
        "field_name": "expenditures",
        "display_name": "Expenditures",
    },
    "fund_name": {
        "field_name": "fund_name.keyword",
        "display_name": "Fund Name",
    },
    "fund_number": {
        "field_name": "fund_number.keyword",
        "display_name": "Fund Number",
    },
    "iba_project_number": {
        "field_name": "iba_project_number.keyword",
        "display_name": "IBA Project Number",
    },
    "lifetime_allotment": {
        "field_name": "lifetime_allotment",
        "display_name": "Lifetime Allotment",
    },
    "lifetime_balance": {
        "field_name": "lifetime_balance",
        "display_name": "Lifetime Balance",
    },
    "lifetime_budget": {
        "field_name": "lifetime_budget",
        "display_name": "Lifetime Budget",
    },
    "master_project_name": {
        "field_name": "master_project_name.keyword",
        "display_name": "Master Project Name",
    },
    "master_project_number": {
        "field_name": "master_project_number.keyword",
        "display_name": "Master Project Number",
    },
    "obligations": {
        "field_name": "obligations",
        "display_name": "Obligations",
    },
    "owner_agency": {
        "field_name": "owner_agency.keyword",
        "display_name": "Owner Agency",
    },
    "parent_task_name": {
        "field_name": "parent_task_name.keyword",
        "display_name": "Parent Task Name",
    },
    "parent_task_number": {
        "field_name": "parent_task_number.keyword",
        "display_name": "Parent Task Number",
    },
    "program": {
        "field_name": "program.keyword",
        "display_name": "Program",
    },
    "program_name": {
        "field_name": "program_name.keyword",
        "display_name": "Program Name",
    },
    "project_end_date": {
        "field_name": "project_end_date",
        "display_name": "Project End Date",
    },
    "project_name": {
        "field_name": "project_name.keyword",
        "display_name": "Project Name",
    },
    "project_number": {
        "field_name": "project_number.keyword",
        "display_name": "Project Number",
    },
    "project_organization": {
        "field_name": "project_organization.keyword",
        "display_name": "Project Organization",
    },
    "project_start_date": {
        "field_name": "project_start_date",
        "display_name": "Project Start Date",
    },
    "project_status": {
        "field_name": "project_status.keyword",
        "display_name": "Project Status",
    },
    "subtask_name": {
        "field_name": "subtask_name.keyword",
        "display_name": "Subtask Name",
    },
    "subtask_number": {
        "field_name": "subtask_number.keyword",
        "display_name": "Sub Task Number",
    },
    "program_parent1": {
        "field_name": "program_parent1.keyword",
        "display_name": "Program Parent 1",
    },
    "program_parent1_description": {
        "field_name": "program_parent1_description.keyword",
        "display_name": "Program Parent 1 Description",
    },
    "project_type": {
        "field_name": "project_type.keyword",
        "display_name": "Project Type",
    },
}

APPROVED_R025_CHART_FIELDS = {
    # r025 index fields
    "agency": {
        "field_name": "agency.keyword",
        "display_name": "Agency",
    },
    "agency_description": {
        "field_name": "agency_description.keyword",
        "display_name": "Agency Description",
    },
    "appropriated_fund": {
        "field_name": "appropriated_fund.keyword",
        "display_name": "Appropriated Fund",
    },
    "appropriated_fund_description": {
        "field_name": "appropriated_fund_description.keyword",
        "display_name": "Appropriated Fund Description",
    },
    "fund": {
        "field_name": "fund.keyword",
        "display_name": "Fund",
    },
    "fund_description": {
        "field_name": "fund_description.keyword",
        "display_name": "Fund Description",
    },
    "account_category_parent_level_3": {
        "field_name": "account_category_parent_level_3.keyword",
        "display_name": "Account Category (Parent Level 3)",
    },
    "account_category_description_parent_level_3": {
        "field_name": "account_category_description_parent_level_3.keyword",
        "display_name": "Account Category Description (Parent Level 3)",
    },
    "account_group_parent_level_1": {
        "field_name": "account_group_parent_level_1.keyword",
        "display_name": "Account Group (Parent Level 1)",
    },
    "account_group_parent_level_1_description": {
        "field_name": "account_group_parent_level_1_description.keyword",
        "display_name": "Account Group (Parent Level 1) Description",
    },
    "account": {
        "field_name": "account.keyword",
        "display_name": "Account",
    },
    "account_description": {
        "field_name": "account_description.keyword",
        "display_name": "Account Description",
    },
    "program_parent_level_2": {
        "field_name": "program_parent_level_2.keyword",
        "display_name": "Program (Parent Level 2)",
    },
    "program_parent_level_2_description": {
        "field_name": "program_parent_level_2_description.keyword",
        "display_name": "Program (Parent Level 2) Description",
    },
    "program_parent_level_1": {
        "field_name": "program_parent_level_1.keyword",
        "display_name": "Program (Parent Level 1)",
    },
    "program_parent_level_1_description": {
        "field_name": "program_parent_level_1_description.keyword",
        "display_name": "Program (Parent Level 1) Description",
    },
    "program": {
        "field_name": "program.keyword",
        "display_name": "Program",
    },
    "program_description": {
        "field_name": "program_description.keyword",
        "display_name": "Program Description",
    },
    "cost_center_parent_level_2": {
        "field_name": "cost_center_parent_level_2.keyword",
        "display_name": "Cost Center (Parent Level 2)",
    },
    "cost_center_parent_level_2_description": {
        "field_name": "cost_center_parent_level_2_description.keyword",
        "display_name": "Cost Center (Parent Level 2) Description",
    },
    "cost_center_parent_level_1": {
        "field_name": "cost_center_parent_level_1.keyword",
        "display_name": "Cost Center (Parent Level 1)",
    },
    "cost_center_parent_level_1_description": {
        "field_name": "cost_center_parent_level_1_description.keyword",
        "display_name": "Cost Center (Parent Level 1) Description",
    },
    "cost_center": {
        "field_name": "cost_center.keyword",
        "display_name": "Cost Center",
    },
    "cost_center_description": {
        "field_name": "cost_center_description.keyword",
        "display_name": "Cost Center Description",
    },
    "project": {
        "field_name": "project.keyword",
        "display_name": "Project",
    },
    "project_description": {
        "field_name": "project_description.keyword",
        "display_name": "Project Description",
    },
    "award_description": {
        "field_name": "award_description.keyword",
        "display_name": "Award Description",
    },
    "initial_budget": {
        "field_name": "initial_budget",
        "display_name": "Initial Budget",
    },
    "adjustment_budget": {
        "field_name": "adjustment_budget",
        "display_name": "Adjustment Budget",
    },
    "total_budget": {
        "field_name": "total_budget",
        "display_name": "Total Budget",
    },
    "commitment": {
        "field_name": "commitment",
        "display_name": "Commitment",
    },
    "obligation": {
        "field_name": "obligation",
        "display_name": "Obligation",
    },
    "expenditure": {
        "field_name": "expenditure",
        "display_name": "Expenditure",
    },
    "budget_reservations": {
        "field_name": "budget_reservations",
        "display_name": "Budget Reservations",
    },
    "available_budget": {
        "field_name": "available_budget",
        "display_name": "Available Budget",
    },
    "award": {
        "field_name": "award.keyword",
        "display_name": "Award",
    },
}

# Common fields that exist across both R085 and R025 indices
COMMON_FIELDS = {
    # Mapped fields that have different names but similar meaning
    "award_name": {
        "field_name": "award_name",
        "display_name": "Award Name",
        "field_type": "keyword",
        "compatible_indices": ["r085_v3", "r025"],
        "is_universal": True,
        "field_mapping": {
            "r085_v3": "award_name.keyword",
            "r025": "award_description.keyword",
        },
    },
    "cost_center": {
        "field_name": "cost_center",
        "display_name": "Cost Center",
        "field_type": "keyword",
        "compatible_indices": ["r085_v3", "r025"],
        "is_universal": True,
        "field_mapping": {
            "r085_v3": "cost_center.keyword",
            "r025": "cost_center.keyword",
        },
    },
    "fund_number": {
        "field_name": "fund_number",
        "display_name": "Fund Number",
        "field_type": "keyword",
        "compatible_indices": ["r085_v3", "r025"],
        "is_universal": True,
        "field_mapping": {"r085_v3": "fund_number.keyword", "r025": "fund.keyword"},
    },
    "fund_name": {
        "field_name": "fund_name",
        "display_name": "Fund Name",
        "field_type": "keyword",
        "compatible_indices": ["r085_v3", "r025"],
        "is_universal": True,
        "field_mapping": {
            "r085_v3": "fund_name.keyword",
            "r025": "fund_description.keyword",
        },
    },
    "project_number": {
        "field_name": "project_number",
        "display_name": "Project Number",
        "field_type": "keyword",
        "compatible_indices": ["r085_v3", "r025"],
        "is_universal": True,
        "field_mapping": {
            "r085_v3": "project_number.keyword",
            "r025": "project.keyword",
        },
    },
    "project_name": {
        "field_name": "project_name",
        "display_name": "Project Name",
        "field_type": "keyword",
        "compatible_indices": ["r085_v3", "r025"],
        "is_universal": True,
        "field_mapping": {
            "r085_v3": "project_name.keyword",
            "r025": "project_description.keyword",
        },
    },
    "total_budget": {
        "field_name": "total_budget",
        "display_name": "Total Budget",
        "field_type": "float",
        "compatible_indices": ["r085_v3", "r025"],
        "is_universal": True,
        "field_mapping": {"r085_v3": "total_project_budget", "r025": "total_budget"},
    },
}

# Field mapping configuration for transforming field names between indices
FIELD_MAPPING_CONFIG = {
    "r085_v3": {
        "award_name.keyword": "award_name",
        "cost_center.keyword": "cost_center",
        "fund_number.keyword": "fund_number",
        "fund_name.keyword": "fund_name",
        "project_number.keyword": "project_number",
        "project_name.keyword": "project_name",
        "total_project_budget": "total_budget",
    },
    "r025": {
        "award_description.keyword": "award_name",
        "cost_center.keyword": "cost_center",
        "fund.keyword": "fund_number",
        "fund_description.keyword": "fund_name",
        "project.keyword": "project_number",
        "project_description.keyword": "project_name",
        "total_budget": "total_budget",
    },
}

# Reverse mapping for easy lookup
REVERSE_FIELD_MAPPING = {
    "award_name": {
        "r085_v3": "award_name.keyword",
        "r025": "award_description.keyword",
    },
    "cost_center": {
        "r085_v3": "cost_center.keyword",
        "r025": "cost_center.keyword",
    },
    "fund_number": {"r085_v3": "fund_number.keyword", "r025": "fund.keyword"},
    "fund_name": {"r085_v3": "fund_name.keyword", "r025": "fund_description.keyword"},
    "project_number": {
        "r085_v3": "project_number.keyword",
        "r025": "project.keyword",
    },
    "project_name": {
        "r085_v3": "project_name.keyword",
        "r025": "project_description.keyword",
    },
    "total_budget": {"r085_v3": "lifetime_budget", "r025": "total_budget"},
}


def get_field_display_name(field_name: str) -> str:
    """Get the display name for a field"""
    # Check in PAR fields first
    for field_info in APPROVED_PAR_CHART_FIELDS.values():
        if field_info["field_name"] == field_name:
            return field_info["display_name"]

    # Then check in R025 fields
    for field_info in APPROVED_R025_CHART_FIELDS.values():
        if field_info["field_name"] == field_name:
            return field_info["display_name"]

    # If not found in either, return formatted field name
    return field_name.replace("_", " ").title()


# Base chart configurations
CHART_CONFIGS = {
    ChartType.BAR: {
        "chart_type": ChartType.BAR,
        "supported_field_types": [
            FieldType.NUMERIC,
            FieldType.TEXT,
            FieldType.DATE,
            FieldType.KEYWORD,
        ],
        "required_fields": {
            "x_axis": [FieldType.TEXT, FieldType.DATE, FieldType.NUMERIC],
            "y_axis": FieldType.NUMERIC,
        },
        "optional_fields": {"group_by": FieldType.TEXT, "color": FieldType.TEXT},
        "supported_aggregations": [
            AggregationType.SUM,
            AggregationType.AVG,
            AggregationType.COUNT,
            AggregationType.DISTINCT_COUNT,
        ],
    },
    ChartType.LINE: {
        "chart_type": ChartType.LINE,
        "supported_field_types": [
            FieldType.NUMERIC,
            FieldType.TEXT,
            FieldType.DATE,
            FieldType.KEYWORD,
        ],
        "required_fields": {
            "x_axis": [FieldType.DATE, FieldType.TEXT, FieldType.NUMERIC],
            "y_axis": FieldType.NUMERIC,
        },
        "optional_fields": {"group_by": FieldType.TEXT},
        "supported_aggregations": [
            AggregationType.SUM,
            AggregationType.AVG,
            AggregationType.MIN,
            AggregationType.MAX,
        ],
    },
    ChartType.NUMBER: {
        "chart_type": ChartType.NUMBER,
        "supported_field_types": [FieldType.NUMERIC],
        "required_fields": {"value": FieldType.NUMERIC},
        "optional_fields": {},
        "supported_aggregations": [
            AggregationType.SUM,
            AggregationType.AVG,
            AggregationType.MIN,
            AggregationType.MAX,
            AggregationType.COUNT,
            AggregationType.DISTINCT_COUNT,
        ],
    },
    ChartType.PIE: {
        "chart_type": ChartType.PIE,
        "supported_field_types": [FieldType.NUMERIC, FieldType.TEXT, FieldType.KEYWORD],
        "required_fields": {
            "value": FieldType.NUMERIC,
            "category": [FieldType.TEXT, FieldType.KEYWORD],
        },
        "optional_fields": {},
        "supported_aggregations": [
            AggregationType.SUM,
            AggregationType.COUNT,
            AggregationType.DISTINCT_COUNT,
        ],
    },
    ChartType.STACKED_BAR: {
        "chart_type": ChartType.STACKED_BAR,
        "supported_field_types": [
            FieldType.NUMERIC,
            FieldType.TEXT,
            FieldType.DATE,
            FieldType.KEYWORD,
        ],
        "required_fields": {
            "x_axis": [FieldType.TEXT, FieldType.DATE, FieldType.NUMERIC],
            "y_axis": FieldType.NUMERIC,
            "stack_by": [FieldType.TEXT, FieldType.KEYWORD],
        },
        "optional_fields": {"color": FieldType.TEXT},
        "supported_aggregations": [
            AggregationType.SUM,
            AggregationType.AVG,
            AggregationType.COUNT,
            AggregationType.DISTINCT_COUNT,
        ],
    },
}

# Base field type aggregations mapping
FIELD_TYPE_AGGREGATIONS = {
    FieldType.NUMERIC: [
        AggregationType.SUM,
        AggregationType.AVG,
        AggregationType.MIN,
        AggregationType.MAX,
        AggregationType.COUNT,
        AggregationType.DISTINCT_COUNT,
    ],
    FieldType.TEXT: [AggregationType.COUNT, AggregationType.DISTINCT_COUNT],
    FieldType.KEYWORD: [AggregationType.COUNT, AggregationType.DISTINCT_COUNT],
    FieldType.DATE: [
        AggregationType.COUNT,
        AggregationType.DISTINCT_COUNT,
        AggregationType.MIN,
        AggregationType.MAX,
    ],
    FieldType.BOOLEAN: [AggregationType.COUNT, AggregationType.DISTINCT_COUNT],
}

# Base validation rules for chart types
BASE_VALIDATION_RULES = {
    ChartType.BAR: {
        "required_fields": ["x_axis", "y_axis"],
        "incompatible_fields": [["x_axis", "group_by"]],
        "dependent_fields": {"group_by": ["y_axis"], "color": ["group_by"]},
        "field_combinations": [
            ["x_axis", "y_axis"],
            ["x_axis", "y_axis", "group_by"],
            ["x_axis", "y_axis", "group_by", "color"],
        ],
        "aggregation_rules": {
            "x_axis": [
                AggregationType.COUNT,
                AggregationType.DISTINCT_COUNT,
                AggregationType.SUM,
                AggregationType.AVG,
                AggregationType.MIN,
                AggregationType.MAX,
            ],
            "y_axis": [AggregationType.SUM, AggregationType.AVG, AggregationType.COUNT],
        },
        "time_granularity_rules": {
            "x_axis": [
                TimeGranularity.YEAR,
                TimeGranularity.QUARTER,
                TimeGranularity.MONTH,
            ]
        },
    },
    ChartType.LINE: {
        "required_fields": ["x_axis", "y_axis"],
        "incompatible_fields": [],
        "dependent_fields": {"group_by": ["y_axis"]},
        "field_combinations": [["x_axis", "y_axis"], ["x_axis", "y_axis", "group_by"]],
        "aggregation_rules": {
            "x_axis": [
                AggregationType.COUNT,
                AggregationType.DISTINCT_COUNT,
                AggregationType.SUM,
                AggregationType.AVG,
                AggregationType.MIN,
                AggregationType.MAX,
            ],
            "y_axis": [
                AggregationType.SUM,
                AggregationType.AVG,
                AggregationType.MIN,
                AggregationType.MAX,
            ],
        },
        "time_granularity_rules": {
            "x_axis": list(TimeGranularity)  # All time granularities supported
        },
    },
    ChartType.PIE: {
        "required_fields": ["value", "category"],
        "incompatible_fields": [],
        "dependent_fields": {},
        "field_combinations": [["value", "category"]],
        "aggregation_rules": {
            "value": [
                AggregationType.SUM,
                AggregationType.COUNT,
                AggregationType.DISTINCT_COUNT,
            ]
        },
        "time_granularity_rules": {},
    },
    ChartType.NUMBER: {
        "required_fields": ["value"],
        "incompatible_fields": [],
        "dependent_fields": {},
        "field_combinations": [["value"]],
        "aggregation_rules": {
            "value": [
                AggregationType.SUM,
                AggregationType.AVG,
                AggregationType.MIN,
                AggregationType.MAX,
                AggregationType.COUNT,
                AggregationType.DISTINCT_COUNT,
            ]
        },
        "time_granularity_rules": {},
    },
    ChartType.STACKED_BAR: {
        "required_fields": ["x_axis", "y_axis", "stack_by"],
        "incompatible_fields": [],
        "dependent_fields": {"color": ["stack_by"]},
        "field_combinations": [
            ["x_axis", "y_axis", "stack_by"],
            ["x_axis", "y_axis", "stack_by", "color"],
        ],
        "aggregation_rules": {
            "x_axis": [
                AggregationType.COUNT,
                AggregationType.DISTINCT_COUNT,
                AggregationType.SUM,
                AggregationType.AVG,
                AggregationType.MIN,
                AggregationType.MAX,
            ],
            "y_axis": [
                AggregationType.SUM,
                AggregationType.AVG,
                AggregationType.COUNT,
                AggregationType.DISTINCT_COUNT,
            ],
        },
        "time_granularity_rules": {
            "x_axis": [
                TimeGranularity.YEAR,
                TimeGranularity.QUARTER,
                TimeGranularity.MONTH,
            ]
        },
    },
}


def _determine_field_type(field_name: str) -> str:
    """Determine field type based on field name patterns"""
    field_lower = field_name.lower()

    # Date fields
    if any(
        date_keyword in field_lower
        for date_keyword in ["date", "created_at", "updated_at"]
    ):
        return "date"

    if any(
        keyword in field_lower
        for keyword in [
            "analyst",
            "manager",
            "sponsor",
            "name",
            "description",
            "type",
            "status",
            "group",
            "category",
            "program",
            "account",
            "organization",
            "location",
            "activity",
            "comment",
            "reason",
            "point",
            "route",
            "asset",
            "improvement",
        ]
    ):
        return "keyword"

    # Numeric fields - but exclude fields that are clearly identifiers
    if any(
        numeric_keyword in field_lower
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
        return "float"

    # Number fields that should be keyword (identifiers)
    if any(
        number_keyword in field_lower
        for number_keyword in [
            "fap_number",
            "project_number",
            "fund_number",
            "contract_number",
            "bridge_number",
            "gis_route_id",
            "recipient_project_number",
            "master_project_number",
            "parent_task_number",
            "subtask_number",
            "award_cfda_no",
            "award_number",
            "iba_project_number",
        ]
    ):
        return "keyword"

    # Boolean fields
    if any(
        bool_keyword in field_lower
        for bool_keyword in ["is_", "has_", "active", "enabled"]
    ):
        return "boolean"

    # Default to keyword for most other fields
    return "keyword"


def _get_supported_filters(field_type: str) -> list:
    """Get supported filter types based on field type"""
    filter_mappings = {
        "text": ["contains", "not_contains", "starts_with", "ends_with"],
        "keyword": [
            "equals",
            "not_equals",
            "in",
            "not_in",
            "contains",
            "not_contains",
            "starts_with",
            "ends_with",
        ],
        "date": [
            "equals",
            "not_equals",
            "range",
            "greater_than",
            "less_than",
        ],
        "datetime": [
            "equals",
            "not_equals",
            "range",
            "greater_than",
            "less_than",
        ],
        "long": [
            "equals",
            "not_equals",
            "greater_than",
            "less_than",
            "between",
            "in",
            "not_in",
        ],
        "integer": [
            "equals",
            "not_equals",
            "greater_than",
            "less_than",
            "between",
            "in",
            "not_in",
        ],
        "float": [
            "equals",
            "not_equals",
            "greater_than",
            "less_than",
            "between",
        ],
        "double": [
            "equals",
            "not_equals",
            "greater_than",
            "less_than",
            "between",
        ],
        "boolean": ["equals", "not_equals"],
        "ip": ["equals", "not_equals", "in", "not_in"],
        "geo_point": ["geo_distance", "geo_bounding_box"],
        "nested": ["nested_query"],
    }

    default_filters = ["equals", "not_equals", "exists", "not_exists"]
    return filter_mappings.get(field_type.lower(), default_filters)


def _enhance_field_info(field_info: dict) -> dict:
    field_name = field_info["field_name"]
    field_type = _determine_field_type(field_name)
    supported_filters = _get_supported_filters(field_type)

    return {
        "field_name": field_name,
        "display_name": field_info["display_name"],
        "field_type": field_type,
        "supported_filters": supported_filters,
    }


def generate_filter_configuration() -> dict:
    """Generate FILTER_CONFIGURATION from existing constants"""
    # Start with common fields
    config = {
        "common": {
            field_key: _enhance_field_info(field_info)
            for field_key, field_info in COMMON_FIELDS.items()
        },
        "r085_v3": {},
        "r025": {},
    }

    # Add R085 fields, but skip any that are already in common fields
    for field_key, field_info in APPROVED_PAR_CHART_FIELDS.items():
        if field_key not in COMMON_FIELDS:
            config["r085_v3"][field_key] = _enhance_field_info(field_info)

    # Add R025 fields, but skip any that are already in common fields
    for field_key, field_info in APPROVED_R025_CHART_FIELDS.items():
        if field_key not in COMMON_FIELDS:
            config["r025"][field_key] = _enhance_field_info(field_info)

    return config


def get_filter_configuration_for_index(index_type: str) -> dict:
    """Generate filter configuration for a specific index type only."""
    if index_type == "common":
        return {
            field_key: _enhance_field_info(field_info)
            for field_key, field_info in COMMON_FIELDS.items()
        }
    elif index_type == "r025":
        config = {
            field_key: _enhance_field_info(field_info)
            for field_key, field_info in APPROVED_R025_CHART_FIELDS.items()
            if field_key not in COMMON_FIELDS
        }
        return config
    else:
        config = {
            field_key: _enhance_field_info(field_info)
            for field_key, field_info in APPROVED_PAR_CHART_FIELDS.items()
            if field_key not in COMMON_FIELDS
        }
        return config
