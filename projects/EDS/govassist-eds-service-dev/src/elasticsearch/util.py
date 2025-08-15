from typing import Any, Dict

from src.services.field_mapping_service import FieldMappingService


def transform_field_filter(field: str, filter_config: Any, data_source: str) -> Dict:
    """Helper to transform a single field filter"""
    field_mapping_service = FieldMappingService()
    transformed_filter = field_mapping_service.transform_filter_field(
        {field: filter_config}, data_source
    )
    transformed_field = list(transformed_filter.keys())[0]
    transformed_config = transformed_filter[transformed_field]

    if isinstance(filter_config, dict) and "operator" in filter_config:
        return {transformed_field: transformed_config}
    else:
        return {
            transformed_field: {
                "operator": (
                    "equals" if not isinstance(transformed_config, list) else "in"
                ),
                "value": transformed_config,
            }
        }
