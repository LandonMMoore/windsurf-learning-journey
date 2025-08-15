from typing import Callable, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.exceptions import BadRequestError, InternalServerError, NotFoundError
from src.model.preconfigured_widget_model import PreconfiguredWidget
from src.repository.dashboard_repository import DashboardRepository
from src.repository.dashboard_widget_repository import DashboardWidgetRepository
from src.schema.dashboard_widget_schema import (
    DashboardWidgetBulkUpdate,
    DashboardWidgetUpdate,
)
from src.schema.preconfigured_widget_schema import (
    PreconfiguredWidgetCreate,
    PreconfiguredWidgetInfo,
)
from src.schema.widget_favorite_schema import WidgetFavoriteFind
from src.services.base_service import BaseService
from src.services.widget_favorite_service import WidgetFavoriteService


class DashboardWidgetService(BaseService):
    def __init__(
        self,
        session_factory: Callable[..., Session],
        widget_favorite_service: Optional[WidgetFavoriteService] = None,
    ):
        super().__init__(DashboardWidgetRepository(session_factory))
        self._widget_favorite_service = widget_favorite_service

    def get_widget_list(
        self,
        find: Optional[dict] = None,
        user_id: Optional[int] = None,
        searchable_fields: Optional[List[str]] = None,
    ) -> dict:
        """Get list of widgets with favorite status for a user.

        Args:
            find: Search and filter criteria
            user_id: ID of the user to check favorites for
            searchable_fields: List of fields to search in

        Returns:
            Dictionary containing the list of widgets with favorite status and search options
        """
        # Get base widget list
        result = self.get_list(find, searchable_fields)

        # If no user_id provided or no favorite service, return without favorite status
        if not user_id or not self._widget_favorite_service:
            return result

        # Get user's favorite widgets_ids
        favorite_widget_ids = self._widget_favorite_service.get_favorite_widget_ids(
            user_id
        )

        # Add favorite status to widgets
        if result.get("founds"):
            for widget in result["founds"]:
                widget.is_favorite = widget.id in favorite_widget_ids

        return result

    def get_widget_by_id(self, id: int, user_id: Optional[int] = None) -> dict:
        """Get a widget by ID with favorite status.

        Args:
            id: The widget ID
            user_id: Optional user ID to check favorite status

        Returns:
            Widget data with favorite status
        """
        widget = self.get_by_id(id)

        # If no user_id provided or no favorite service, return without favorite status
        if not user_id or not self._widget_favorite_service:
            return widget

        # Check if widget is favorited by user
        find_favorite = WidgetFavoriteFind(user_id=user_id)
        favorite_widgets = self._widget_favorite_service.get_user_favorites(
            user_id, find_favorite
        )

        favorite_widget_ids = {w.widget.id for w in favorite_widgets.get("founds", [])}

        widget.is_favorite = widget.id in favorite_widget_ids
        return widget

    def bulk_update(self, data: DashboardWidgetBulkUpdate) -> List[dict]:
        """Update multiple dashboard widgets in bulk.

        Args:
            data: The bulk update data containing dashboard_id and list of widgets with position information

        Returns:
            List of updated widget objects
        """
        updated_widgets = []

        with self._repository.session_factory() as session:
            try:
                # Verify all widgets belong to the same dashboard
                for widget_data in data.widgets:
                    widget = (
                        session.query(self._repository.model)
                        .filter(
                            self._repository.model.id == widget_data.id,
                            self._repository.model.dashboard_id == data.dashboard_id,
                        )
                        .first()
                    )

                    if not widget:
                        raise NotFoundError(
                            f"Widget with ID {widget_data.id} not found or does not belong to dashboard {data.dashboard_id}"
                        )

                # Update each widget's position data
                for widget_data in data.widgets:
                    # Create a proper update schema excluding the id field
                    update_data = widget_data.dict(exclude_none=True, exclude={"id"})

                    if update_data:  # Only update if there are actual changes
                        update_schema = DashboardWidgetUpdate(**update_data)
                        widget = self.patch(widget_data.id, update_schema)
                        updated_widgets.append(widget)

                return updated_widgets

            except HTTPException:
                # Re-raise HTTPException subclasses (like NotFoundError) without modification
                session.rollback()
                raise
            except Exception:
                session.rollback()
                raise InternalServerError(detail="Internal Server Error")

    def clone_widget(self, widget_data: dict, dashboard_id: int) -> dict:
        """Clone a widget to a specified dashboard."""
        with self._repository.session_factory() as session:
            try:
                if hasattr(widget_data, "__dict__"):
                    widget_dict = widget_data.__dict__
                else:
                    widget_dict = widget_data.copy()

                fields_to_remove = [
                    "id",
                    "is_favorite",
                    "uuid",
                    "created_at",
                    "updated_at",
                ]
                widget_dict = {
                    key: value
                    for key, value in widget_dict.items()
                    if not key.startswith("_") and key not in fields_to_remove
                }
                # Alter name to append "Copy"
                widget_dict["name"] = f"{widget_dict['name']} (Copy)"

                dashboard_repo = DashboardRepository(self._repository.session_factory)
                if not dashboard_repo.read_by_id(dashboard_id):
                    raise NotFoundError(f"Dashboard with ID {dashboard_id} not found")

                new_widget = self._repository.model(**widget_dict)
                new_widget.dashboard_id = dashboard_id

                session.add(new_widget)
                session.commit()
                session.refresh(new_widget)

                return new_widget
            except HTTPException:
                # Re-raise HTTPException subclasses (like NotFoundError) without modification
                session.rollback()
                raise
            except Exception:
                session.rollback()
                raise InternalServerError(detail="Internal Server Error")

    def save_dashboard_widget_as_preconfigured_widget(
        self, preconfigured_widget: PreconfiguredWidgetCreate
    ) -> PreconfiguredWidgetInfo:
        """Save a dashboard widget as a preconfigured widget."""
        with self._repository.session_factory() as session:
            dashboard_widget = self.get_by_id(preconfigured_widget.dashboard_widget_id)
            if not dashboard_widget:
                raise NotFoundError(
                    f"Widget with ID {preconfigured_widget.dashboard_widget_id} not found"
                )

            preconfigured_widget = PreconfiguredWidget(
                name=preconfigured_widget.widget_name,
                description=preconfigured_widget.widget_description,
                widget_type=dashboard_widget.widget_type,
                image_url=dashboard_widget.image_url,
                data_source=dashboard_widget.data_source,
                config=dashboard_widget.config,
                filters=dashboard_widget.filters,
                category=preconfigured_widget.category,
                category_label=preconfigured_widget.category,
            )
            session.add(preconfigured_widget)
            session.commit()
            session.refresh(preconfigured_widget)
            return preconfigured_widget

    def delete_preconfigured_widget(self, preconfigured_widget_id: int) -> dict:
        """Delete a preconfigured widget."""
        with self._repository.session_factory() as session:
            preconfigured_widget = (
                session.query(PreconfiguredWidget)
                .filter(PreconfiguredWidget.id == preconfigured_widget_id)
                .first()
            )
            if not preconfigured_widget:
                raise NotFoundError(
                    f"Preconfigured widget with ID {preconfigured_widget_id} not found"
                )

            if preconfigured_widget.category in ["r025", "custom", "eds_system"]:
                raise BadRequestError(
                    f"Deletion not allowed for preconfigured widget with ID '{preconfigured_widget_id}': classified as a system widget"
                )

            session.delete(preconfigured_widget)
            session.commit()
            return {"message": "Preconfigured widget deleted successfully"}
