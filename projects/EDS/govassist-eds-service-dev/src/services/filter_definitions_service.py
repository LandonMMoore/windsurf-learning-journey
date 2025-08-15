from typing import List, Optional

from src.model.filter_definitions import FilterField, FilterOperator, FilterType


class FilterDefinitionsService:
    """
    Simplified service for filter definitions
    """

    def get_filter_definitions(self) -> List[FilterField]:
        """
        Get filter definitions. In production, these would come from
        database or configuration based on actual Elasticsearch mappings.
        """
        # This method can be extended to load real filter definitions
        # from Elasticsearch mappings or database configuration
        return [
            self.build_filter_field(
                field="status",
                label="Status",
                type=FilterType.ENUM,
                group="General",
                values=["active", "inactive", "pending", "completed"],
            ),
            self.build_filter_field(
                field="created_at",
                label="Created Date",
                type=FilterType.DATE,
                group="General",
            ),
            self.build_filter_field(
                field="amount",
                label="Amount",
                type=FilterType.NUMBER,
                group="Financial",
            ),
            self.build_filter_field(
                field="name",
                label="Name",
                type=FilterType.STRING,
                group="General",
            ),
            self.build_filter_field(
                field="is_archived",
                label="Archived",
                type=FilterType.BOOLEAN,
                group="General",
            ),
        ]

    @staticmethod
    def build_filter_field(
        field: str,
        label: str,
        type: FilterType,
        group: str,
        operators: Optional[List[FilterOperator]] = None,
        values: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> FilterField:
        """
        Helper method to build a filter field
        """
        return FilterField(
            field=field,
            label=label,
            type=type,
            group=group,
            operators=operators or [],
            values=values,
            description=description,
        )
