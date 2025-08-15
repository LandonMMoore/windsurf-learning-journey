from fastapi import HTTPException

from src.repository.dashboard_widget_repository import DashboardWidgetRepository
from src.repository.widget_favorite_repository import WidgetFavoriteRepository
from src.schema.base_schema import FindBase
from src.schema.widget_favorite_schema import WidgetFavoriteToggleResponse


class WidgetFavoriteService:
    def __init__(
        self,
        widget_favorite_repository: WidgetFavoriteRepository,
        dashboard_widget_repository: DashboardWidgetRepository,
    ):
        self.widget_favorite_repository = widget_favorite_repository
        self.dashboard_widget_repository = dashboard_widget_repository

    def toggle_favorite(
        self, user_id: int, widget_id: int
    ) -> WidgetFavoriteToggleResponse:
        """
        Toggle favorite status for a widget.

        Args:
            user_id: The ID of the user performing the action
            widget_id: The ID of the widget to toggle

        Returns:
            WidgetFavoriteToggleResponse with the updated favorite status

        Raises:
            HTTPException: If the widget doesn't exist
        """
        # Verify widget exists
        widget = self.dashboard_widget_repository.read_by_id(widget_id)
        if not widget:
            raise HTTPException(
                status_code=404, detail=f"Widget with id {widget_id} not found"
            )

        # Toggle favorite status
        is_favorite = self.widget_favorite_repository.toggle_favorite(
            user_id, widget_id
        )

        return WidgetFavoriteToggleResponse(
            widget_id=widget_id, is_favorite=is_favorite
        )

    def get_user_favorites(self, user_id: int, find: FindBase) -> dict:
        """
        Get all favorited widgets for a user.

        Args:
            user_id: The ID of the user
            find: The find options for pagination and sorting

        Returns:
            Dictionary containing the list of favorited widgets and search options
        """
        return self.widget_favorite_repository.get_user_favorites(user_id, find)

    def get_favorite_widget_ids(self, user_id: int) -> set:
        """Get a set of favorite widget IDs for a user."""
        return self.widget_favorite_repository.get_favorite_widget_ids(user_id)
