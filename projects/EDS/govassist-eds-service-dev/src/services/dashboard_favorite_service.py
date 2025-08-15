from src.core.exceptions import NotFoundError
from src.repository.dashboard_favorite_repository import DashboardFavoriteRepository
from src.repository.dashboard_repository import DashboardRepository
from src.schema.dashboard_favorite_schema import (
    DashboardFavoriteFind,
    DashboardFavoriteListResponse,
    DashboardFavoriteToggleResponse,
)


class DashboardFavoriteService:
    def __init__(
        self,
        dashboard_favorite_repository: DashboardFavoriteRepository,
        dashboard_repository: DashboardRepository,
    ):
        self.dashboard_favorite_repository = dashboard_favorite_repository
        self.dashboard_repository = dashboard_repository

    def toggle_favorite(
        self,
        user_id: int,
        dashboard_id: int,
    ) -> DashboardFavoriteToggleResponse:
        """
        Toggle favorite status for a dashboard.

        Args:
            user_id: The ID of the user performing the action
            dashboard_id: The ID of the dashboard to toggle

        Returns:
            DashboardFavoriteToggleResponse with the updated favorite status

        Raises:
            HTTPException: If the dashboard doesn't exist
        """

        dashboard = self.dashboard_repository.read_by_id(dashboard_id)
        if not dashboard:
            raise NotFoundError(f"Dashboard with id {dashboard_id} not found")

        is_favorite = self.dashboard_favorite_repository.toggle_favorite(
            user_id=user_id,
            dashboard_id=dashboard_id,
        )

        return DashboardFavoriteToggleResponse(
            dashboard_id=dashboard_id,
            is_favorite=is_favorite,
        )

    def get_user_favorites(
        self,
        user_id: int,
        find: DashboardFavoriteFind,
    ) -> DashboardFavoriteListResponse:
        """
        Get all favorited dashboards for a user.

        """
        return self.dashboard_favorite_repository.get_user_favorites(user_id, find)
