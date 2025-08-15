from datetime import date, datetime
from typing import Dict, Optional

from src.util.snake_to_title import snake_to_title


def get_column_type(column):
    python_type = column.type.python_type
    type_mapping = {
        str: "string",
        int: "integer",
        float: "float",
        bool: "boolean",
        datetime: "date",
        date: "date",
    }
    if python_type.__name__ in {"dict"}:
        return None
    elif python_type in type_mapping:

        return type_mapping[python_type]
    else:
        raise ValueError(f"Unknown column type: {python_type} for column {column.name}")


MODEL_PRETTY_CONFIG: Dict[str, str] = {
    "master_project_details": "project",
    "master_parent_tasks": "parent_task",
    "master_sub_tasks": "sub_task",
    "master_transactions": "transaction",
    "master_awards": "award",
    "master_funds": "fund",
    "master_sponsors": "sponsor",
    "master_cost_centers": "cost_center",
    "master_programs": "program",
    "master_accounts": "account",
}
REVERSE_MODEL_PRETTY_CONFIG = {v: k for k, v in MODEL_PRETTY_CONFIG.items()}


def get_pretty_table_name(table_name):
    if table_name not in MODEL_PRETTY_CONFIG:
        raise ValueError(f"Unknown table name: {table_name}")
    return MODEL_PRETTY_CONFIG[table_name]


def get_original_table_name(table_name):
    if table_name not in REVERSE_MODEL_PRETTY_CONFIG:
        raise ValueError(f"Unknown pretty table name: {table_name}")
    return REVERSE_MODEL_PRETTY_CONFIG[table_name]


def is_foreign_key(column):
    """Check if a column is a foreign key by examining its foreign_keys attribute."""
    return bool(column.foreign_keys)


def get_fields_from_models(
    table_config: dict,
    searchable_fields: list[str],
    search: str = None,
    ordering: Optional[str] = None,
) -> list[str]:
    all_fields = []
    for table in table_config.items():
        model = table[1].get("model")
        exclude_fields = table[1].get("exclude_fields", {})
        for field in model.__table__.columns:
            column_name = field.name
            column_type = get_column_type(field)
            # Skip foreign key fields
            if (
                is_foreign_key(field)
                or column_name in exclude_fields
                or column_type is None
            ):
                continue
            field_data = {
                "display_column_name": field.info.get(
                    "display_name",
                    model.__col_name_prefix__ + " " + snake_to_title(column_name),
                ),
                "type": column_type,
                "column_name": column_name,
                "table_name": get_pretty_table_name(table[0]),
                "expression": f"{get_pretty_table_name(table[0])}.{column_name}",
            }

            # Apply search filter if search is provided
            if search:
                matches_search = any(
                    search.lower() in field_data[field_name].lower()
                    for field_name in searchable_fields
                    if field_name in field_data
                )
                if not matches_search:
                    continue

            all_fields.append(field_data)

    if ordering:
        reverse = ordering.startswith("-")
        key = ordering.lstrip("-")
        if key not in [
            "column_name",
            "type",
            "table_name",
            "display_column_name",
            "expression",
        ]:
            raise ValueError(f"Invalid ordering key: {key}")
        all_fields.sort(key=lambda f: f[key], reverse=reverse)

    return all_fields
