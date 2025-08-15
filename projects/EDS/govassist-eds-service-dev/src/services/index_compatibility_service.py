"""
Index Compatibility Service - Simplified Elasticsearch Mapping Fetcher

This service provides basic field mapping functionality for dashboard filters.
"""

from typing import Any, Dict, List

from src.elasticsearch.client import create_es_client
from src.elasticsearch.constants import COMMON_FIELDS


class IndexCompatibilityService:
    """
    Simplified service for Elasticsearch field operations
    """

    def __init__(self):
        self.es_client = None

    async def _get_es_client(self):
        """Get Elasticsearch client"""
        if not self.es_client:
            self.es_client = await create_es_client()
        return self.es_client

    async def fetch_index_mapping(self, index_name: str) -> Dict[str, Any]:
        """Fetch mapping directly from Elasticsearch"""
        try:
            es_client = await self._get_es_client()

            # Fetch mapping from Elasticsearch
            response = await es_client.indices.get_mapping(index=index_name)

            if index_name in response:
                mapping = response[index_name]
            else:
                mapping = response

            return mapping

        except Exception:
            return {"mappings": {"properties": {}}}

    def _get_actual_field_type(self, field_config: Dict[str, Any]) -> str:
        """
        Get the actual filterable field type from Elasticsearch field configuration

        Args:
            field_config: Field configuration from Elasticsearch mapping

        Returns:
            Actual field type for filtering (keyword, text, long, etc.)
        """
        # Check for explicit type first
        if "type" in field_config:
            return field_config["type"]

        # Check for fields (indicates text field with keyword mapping)
        if "fields" in field_config:
            # If it has keyword mapping, return keyword for filtering
            if "keyword" in field_config["fields"]:
                return "keyword"
            return "text"

        # Check for properties (object type) - we'll handle this in flattening
        if "properties" in field_config:
            return "object"

        # Default fallback
        return "unknown"

    def _flatten_object_fields(
        self, properties: Dict[str, Any], prefix: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Flatten object fields to show individual filterable fields

        Args:
            properties: Object properties from Elasticsearch mapping
            prefix: Field name prefix for nested fields

        Returns:
            List of flattened field configurations
        """
        flattened_fields = []

        for field_name, field_config in properties.items():
            full_field_name = f"{prefix}.{field_name}" if prefix else field_name

            # Get the actual field type
            field_type = self._get_actual_field_type(field_config)

            # If it's an object with properties, recursively flatten
            if field_type == "object" and "properties" in field_config:
                nested_fields = self._flatten_object_fields(
                    field_config["properties"], full_field_name
                )
                flattened_fields.extend(nested_fields)
            else:
                # This is a filterable field
                flattened_fields.append(
                    {
                        "field_name": full_field_name,
                        "field_type": field_type,
                        "mapping_details": field_config,
                    }
                )

        return flattened_fields

    async def is_field_compatible(self, field_name: str, indices: List[str]) -> bool:
        """Check if a field exists in specified indices"""
        try:
            for index_name in indices:
                mapping = await self.fetch_index_mapping(index_name)
                properties = mapping.get("mappings", {}).get("properties", {})
                if field_name not in properties:
                    return False
            return True
        except Exception:
            return False

    async def get_universal_fields(
        self, indices: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get fields that exist in all specified indices"""
        if indices is None:
            indices = ["r085", "r025", "r085_v3"]

        try:
            # Use predefined common fields from constants
            universal_fields = []
            for field_key, field_info in COMMON_FIELDS.items():
                # Check if the field is compatible with the requested indices
                if all(index in field_info["compatible_indices"] for index in indices):
                    field_data = {
                        "field_name": field_info["field_name"],
                        "field_type": field_info["field_type"],
                        "compatible_indices": field_info["compatible_indices"],
                        "mapping_details": {},
                        "display_name": field_info["display_name"],
                        "is_universal": field_info["is_universal"],
                    }

                    # Add field mapping information if available
                    if "field_mapping" in field_info:
                        field_data["field_mapping"] = field_info["field_mapping"]

                    universal_fields.append(field_data)

            return universal_fields

        except Exception:
            return []

    async def get_index_specific_fields(
        self, index_name: str, indices: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all fields from a particular index (not just unique ones)"""
        if indices is None:
            indices = ["r085", "r025", "r085_v3"]

        try:
            # Get all flattened fields from the requested index
            mapping = await self.fetch_index_mapping(index_name)
            properties = mapping.get("mappings", {}).get("properties", {})

            # Flatten all fields including nested objects
            flattened_fields = self._flatten_object_fields(properties)

            specific_fields = []
            for field_info in flattened_fields:
                specific_fields.append(
                    {
                        "field_name": field_info["field_name"],
                        "field_type": field_info["field_type"],
                        "mapping_details": field_info["mapping_details"],
                    }
                )

            return specific_fields

        except Exception:
            return []
