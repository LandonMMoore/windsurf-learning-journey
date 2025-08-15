import json
from typing import Dict, List, Optional, Union

from loguru import logger

from src.elasticsearch.filter_utils import build_filtered_query
from src.elasticsearch.util import transform_field_filter
from src.services.field_mapping_service import FieldMappingService


class FilterIntegrationService:
    """Service for integrating filters with widget-level filters"""

    def __init__(self, index_compatibility_service=None):
        self.index_compatibility_service = index_compatibility_service
        self.field_mapping_service = FieldMappingService()

    def build_enhanced_query(
        self,
        widget_config: dict,
        dashboard_id: int,
        base_filters: Optional[Union[Dict, List]] = None,
        filter: Optional[dict] = None,
    ) -> dict:
        """Build an enhanced Elasticsearch query with filters"""
        try:
            # Get widget's data source
            data_source = widget_config.get("data_source")
            if not data_source:
                return build_filtered_query(base_filters)

            # Extract widget config filters
            widget_filters = widget_config.get("config", {})

            dashboard_filters = filter or self._get_dashboard_filters(dashboard_id)

            # Build combined filters with new logic
            combined_filters = self._build_combined_filters(
                dashboard_filters, data_source, base_filters, widget_filters
            )

            # Transform filters for the specific data source
            transformed_filters = (
                self.field_mapping_service.transform_filters_for_index(
                    combined_filters, data_source
                )
            )

            # Build the enhanced query with transformed filters
            query = build_filtered_query(transformed_filters)
            return query

        except Exception:
            return build_filtered_query(base_filters)

    def _get_dashboard_filters(self, dashboard_id: int) -> Optional[Dict]:
        """Fetch dashboard filters"""
        try:
            # Import here to avoid circular imports
            from src.core.container import Container
            from src.repository.dashboard_repository import DashboardRepository

            # Get session factory from container
            session_factory = Container.session_factory()

            # Create dashboard repository
            dashboard_repo = DashboardRepository(session_factory)

            # Fetch dashboard with filters
            with session_factory() as session:
                dashboard = (
                    session.query(dashboard_repo.model)
                    .filter_by(id=dashboard_id)
                    .first()
                )

                if not dashboard or not dashboard.filters:
                    return None

                return dashboard.filters

        except Exception as e:
            logger.error(f"Error fetching dashboard filters: {str(e)}")

    def _deduplicate_conditions(self, conditions):
        """Deduplicate a list of dict conditions by their JSON representation."""
        seen = set()
        unique = []
        for cond in conditions:
            cond_str = json.dumps(cond, sort_keys=True)
            if cond_str not in seen:
                seen.add(cond_str)
                unique.append(cond)
        return unique

    def _build_combined_filters(
        self,
        dashboard_filters: Optional[Dict],
        data_source: str,
        base_filters: Optional[Union[Dict, List]],
        widget_filters: Optional[Union[Dict, List]] = None,
    ) -> Optional[Union[Dict, List]]:
        """Build combined filters: dashboard filters AND widget config filters AND base filters"""
        try:
            # Initialize combined conditions
            combined_conditions = []
            # 1. Add base filters (if any)
            if (
                base_filters
                and "data_source_filters" in base_filters
                and data_source in base_filters["data_source_filters"]
            ):
                extracted = base_filters["data_source_filters"][data_source]
                combined_conditions.append(extracted)
            # 2. Add dashboard filters (if any)
            if dashboard_filters:
                dashboard_conditions = self._extract_dashboard_filter_conditions(
                    dashboard_filters, data_source
                )

                # Check if there's an operator specified between data_source_filters and common_filters
                if dashboard_conditions and len(dashboard_conditions) > 1:
                    # Check if operator is specified in dashboard_filters
                    operator = dashboard_filters.get("operator", "and").lower()

                    if operator == "or":
                        # Group data_source and common filters with OR logic
                        dashboard_condition_group = {
                            "operator": "or",
                            "conditions": dashboard_conditions,
                        }
                        combined_conditions.append(dashboard_condition_group)
                    else:
                        # Default to AND logic - add conditions individually
                        combined_conditions.extend(dashboard_conditions)
                else:
                    # Single condition or no conditions
                    combined_conditions.extend(dashboard_conditions)
            # 3. Add widget config filters (if any)
            # if widget_filters:
            #     widget_conditions = self._extract_widget_filter_conditions(
            #         widget_filters, data_source
            #     )
            #     combined_conditions.extend(widget_conditions)

            # 4. Build the final combined filter structure
            if not combined_conditions:
                return None

            # Deduplicate here
            combined_conditions = self._deduplicate_conditions(combined_conditions)

            if len(combined_conditions) == 1:
                return combined_conditions[0]

            # Multiple conditions - use AND logic
            return {"operator": "and", "conditions": combined_conditions}

        except Exception as e:
            logger.error(f"Error building combined filters: {str(e)}")
            return base_filters

    def _extract_dashboard_filter_conditions(
        self, dashboard_filters: Dict, data_source: str
    ) -> List[Dict]:
        """Extract conditions from dashboard filters"""
        conditions = []

        # Add common filters (apply to all data sources)
        common_filters = dashboard_filters.get("common_filters", {})
        if isinstance(common_filters, dict) and "operator" in common_filters:
            transformed_filters = self.field_mapping_service.transform_filter_field(
                common_filters, data_source
            )
            conditions.append(transformed_filters)
        else:
            for field, filter_config in common_filters.items():
                conditions.append(
                    transform_field_filter(field, filter_config, data_source)
                )

        # Add data source specific filters
        data_source_filters = dashboard_filters.get("data_source_filters", {})
        if data_source in data_source_filters:
            source_filters = data_source_filters[data_source]

            if isinstance(source_filters, dict) and "operator" in source_filters:
                transformed_filters = self.field_mapping_service.transform_filter_field(
                    source_filters, data_source
                )
                conditions.append(transformed_filters)
            else:
                for field, filter_config in source_filters.items():
                    conditions.append(
                        transform_field_filter(field, filter_config, data_source)
                    )

        return conditions

    def _extract_widget_filter_conditions(
        self, widget_filters: Union[Dict, List], data_source: str = None
    ) -> List[Dict]:
        """Extract conditions from widget config filters"""
        conditions = []

        if isinstance(widget_filters, dict):
            # Handle complex filter structure with operator and conditions
            if "operator" in widget_filters and "conditions" in widget_filters:
                # This is already in the correct format
                if data_source:
                    transformed_filter = (
                        self.field_mapping_service.transform_filter_field(
                            widget_filters, data_source
                        )
                    )
                    conditions.append(transformed_filter)
                else:
                    conditions.append(widget_filters)
            else:
                # Handle simple field-based filters
                for field, filter_config in widget_filters.items():
                    if isinstance(filter_config, dict) and "operator" in filter_config:
                        if data_source:
                            transformed_filter = (
                                self.field_mapping_service.transform_filter_field(
                                    {field: filter_config}, data_source
                                )
                            )
                            transformed_field = list(transformed_filter.keys())[0]
                            transformed_config = transformed_filter[transformed_field]
                            conditions.append({transformed_field: transformed_config})
                        else:
                            conditions.append({field: filter_config})
                    else:
                        if data_source:
                            transformed_filter = (
                                self.field_mapping_service.transform_filter_field(
                                    {field: filter_config}, data_source
                                )
                            )
                            transformed_field = list(transformed_filter.keys())[0]
                            transformed_config = transformed_filter[transformed_field]
                            # Convert simple value to filter format
                            conditions.append(
                                {
                                    transformed_field: {
                                        "operator": (
                                            "equals"
                                            if not isinstance(transformed_config, list)
                                            else "in"
                                        ),
                                        "value": transformed_config,
                                    }
                                }
                            )
                        else:
                            # Convert simple value to filter format
                            conditions.append(
                                {
                                    field: {
                                        "operator": (
                                            "equals"
                                            if not isinstance(filter_config, list)
                                            else "in"
                                        ),
                                        "value": filter_config,
                                    }
                                }
                            )
        elif isinstance(widget_filters, list):
            # Handle list of filter conditions
            if data_source:
                transformed_filters = (
                    self.field_mapping_service.transform_filters_for_index(
                        widget_filters, data_source
                    )
                )
                conditions.extend(transformed_filters)
            else:
                conditions.extend(widget_filters)

        return conditions

    def _combine_filters(
        self,
        dashboard_filters: Optional[Dict],
        widget_filters: Optional[Union[Dict, List]],
    ) -> Optional[Union[Dict, List]]:
        """Legacy method - kept for backward compatibility"""
        return self._build_combined_filters(dashboard_filters, "", widget_filters, None)

    def _convert_dict_filters_to_list(self, filters_dict: dict) -> List[Dict]:
        """Convert dictionary-style filters to list format"""
        filter_list = []

        for field, value in filters_dict.items():
            if not value or value is None:
                continue

            if isinstance(value, dict):
                # Handle complex filter conditions
                filter_list.append(value)
            else:
                # Handle simple key-value filters
                filter_list.append(
                    {
                        "field": field,
                        "operator": "equals" if not isinstance(value, list) else "in",
                        "value": value,
                    }
                )

        return filter_list

    def _is_filter_applicable(self, filter_item: Union[dict], data_source: str) -> bool:
        """Check if a filter is applicable to the given data source"""
        try:
            # Check if filter has data source restriction
            if "data_source" in filter_item:
                return filter_item["data_source"] == data_source

            # Check if filter has index restriction
            if "index" in filter_item:
                return filter_item["index"] == data_source

            # If no data source restriction, filter is applicable
            return True

        except Exception as e:
            logger.error(f"Error checking filter applicability: {str(e)}")
            return True

    def _transform_filter_for_index(
        self, filter_item: Union[dict], data_source: str
    ) -> dict:
        """Transform filter for specific index/data source"""
        try:
            # Create a copy of the filter item
            transformed_filter = filter_item.copy()

            # Remove data source specific fields
            transformed_filter.pop("data_source", None)
            transformed_filter.pop("index", None)

            return transformed_filter

        except Exception as e:
            logger.error(f"Error transforming filter for index: {str(e)}")
            return filter_item
