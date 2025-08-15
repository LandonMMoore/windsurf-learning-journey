"""
Field Mapping Service

This service handles field name mapping between different Elasticsearch indices
to support common fields across indices with different field names.
"""

from typing import Dict, List, Union

from loguru import logger

from src.elasticsearch.constants import FIELD_MAPPING_CONFIG, REVERSE_FIELD_MAPPING


class FieldMappingService:
    """
    Service for mapping field names between different indices
    """

    def __init__(self):
        self.field_mapping_config = FIELD_MAPPING_CONFIG
        self.reverse_field_mapping = REVERSE_FIELD_MAPPING

    def get_mapped_field_name(self, field_name: str, target_index: str) -> str:
        """
        Get the mapped field name for a given field in a target index

        Args:
            field_name: The common field name (e.g., 'award_name')
            target_index: The target index name (e.g., 'r085' or 'r025')

        Returns:
            The actual field name in the target index
        """
        try:
            if field_name in self.reverse_field_mapping:
                return self.reverse_field_mapping[field_name].get(
                    target_index, field_name
                )
        except Exception as e:
            logger.error(
                f"Error getting mapped field name for {field_name} in {target_index}: {str(e)}"
            )
        return field_name

    def get_common_field_name(self, actual_field_name: str, source_index: str) -> str:
        """
        Get the common field name from an actual field name in a source index

        Args:
            actual_field_name: The actual field name in the source index
            source_index: The source index name (e.g., 'r085' or 'r025')

        Returns:
            The common field name
        """
        try:
            if source_index in self.field_mapping_config:
                return self.field_mapping_config[source_index].get(
                    actual_field_name, actual_field_name
                )
        except Exception as e:
            logger.error(
                f"Error getting common field name for {actual_field_name} in {source_index}: {str(e)}"
            )
        return actual_field_name

    def transform_filter_field(self, filter_config: Dict, target_index: str) -> Dict:
        """
        Transform a filter configuration to use the correct field name for the target index

        Args:
            filter_config: The filter configuration dictionary
            target_index: The target index name

        Returns:
            Transformed filter configuration
        """
        try:
            if not filter_config:
                return filter_config

            transformed_filter = filter_config.copy()

            # Handle different filter structures
            if "field" in transformed_filter:
                # Simple filter structure: {"field": "award_name", "operator": "equals", "value": "test"}
                common_field_name = transformed_filter["field"]
                mapped_field_name = self.get_mapped_field_name(
                    common_field_name, target_index
                )
                transformed_filter["field"] = mapped_field_name

            elif (
                "operator" in transformed_filter and "conditions" in transformed_filter
            ):
                # Complex filter structure with conditions
                transformed_conditions = []
                for condition in transformed_filter["conditions"]:
                    transformed_condition = self.transform_filter_field(
                        condition, target_index
                    )
                    transformed_conditions.append(transformed_condition)
                transformed_filter["conditions"] = transformed_conditions

            elif "field_conditions" in transformed_filter:
                # Handle field_conditions structure: {"field_conditions": {"agency": {"operator": "equals", "value": "KA0"}}}
                field_conditions = transformed_filter["field_conditions"]
                transformed_field_conditions = {}
                for field_name, field_config in field_conditions.items():
                    mapped_field_name = self.get_mapped_field_name(
                        field_name, target_index
                    )
                    transformed_field_conditions[mapped_field_name] = field_config
                transformed_filter["field_conditions"] = transformed_field_conditions

            else:
                # Field-based filter structure: {"award_name": {"operator": "equals", "value": "test"}}
                for field_name, field_config in list(transformed_filter.items()):
                    if isinstance(field_config, dict):
                        # This is a field with filter configuration
                        mapped_field_name = self.get_mapped_field_name(
                            field_name, target_index
                        )
                        if mapped_field_name != field_name:
                            transformed_filter[mapped_field_name] = field_config
                            del transformed_filter[field_name]
                    else:
                        # This is a simple field-value pair
                        mapped_field_name = self.get_mapped_field_name(
                            field_name, target_index
                        )
                        if mapped_field_name != field_name:
                            transformed_filter[mapped_field_name] = field_config
                            del transformed_filter[field_name]

            return transformed_filter

        except Exception as e:
            logger.error(f"Error transforming filter field: {str(e)}")
            return filter_config

    def transform_filters_for_index(
        self, filters: Union[Dict, List], target_index: str
    ) -> Union[Dict, List]:
        """
        Transform a list or dictionary of filters for a specific index

        Args:
            filters: The filters to transform (can be dict or list)
            target_index: The target index name

        Returns:
            Transformed filters
        """
        try:
            if not filters:
                return filters

            if isinstance(filters, list):
                # Transform each filter in the list
                transformed_filters = []
                for filter_item in filters:
                    transformed_filter = self.transform_filter_field(
                        filter_item, target_index
                    )
                    transformed_filters.append(transformed_filter)
                return transformed_filters

            elif isinstance(filters, dict):
                # Transform the filter dictionary
                return self.transform_filter_field(filters, target_index)

            return filters

        except Exception as e:
            logger.error(
                f"Error transforming filters for index {target_index}: {str(e)}"
            )
            return filters

    def is_mapped_field(self, field_name: str) -> bool:
        """
        Check if a field name is a mapped field

        Args:
            field_name: The field name to check

        Returns:
            True if the field is mapped, False otherwise
        """
        return field_name in self.reverse_field_mapping

    def get_all_mapped_fields(self) -> Dict[str, Dict[str, str]]:
        """
        Get all mapped fields and their index-specific names

        Returns:
            Dictionary of mapped fields
        """
        return self.reverse_field_mapping.copy()

    def get_mapped_fields_for_index(self, index_name: str) -> Dict[str, str]:
        """
        Get all mapped fields for a specific index

        Args:
            index_name: The index name

        Returns:
            Dictionary mapping common field names to index-specific field names
        """
        try:
            if index_name in self.field_mapping_config:
                return self.field_mapping_config[index_name].copy()
        except Exception as e:
            logger.error(
                f"Error getting mapped fields for index {index_name}: {str(e)}"
            )
        return {}
