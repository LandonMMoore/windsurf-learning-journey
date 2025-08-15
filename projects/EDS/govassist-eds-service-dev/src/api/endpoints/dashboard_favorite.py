from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.core.dependencies import get_current_user
from src.schema.dashboard_favorite_schema import (
    DashboardFavoriteFind,
    DashboardFavoriteListResponse,
    DashboardFavoriteToggleResponse,
)
from src.services.dashboard_favorite_service import DashboardFavoriteService

router = APIRouter(prefix="/dash-favorites", tags=["Dashboard Favorites"])


@router.post("/{dashboard_id}/favorite", response_model=DashboardFavoriteToggleResponse)
@inject
async def toggle_dashboard_favorite(
    dashboard_id: int,
    current_user: dict = Depends(get_current_user),
    service: DashboardFavoriteService = Depends(
        Provide[Container.dashboard_favorite_service]
    ),
) -> DashboardFavoriteToggleResponse:
    """
    Toggle favorite status for a dashboard.

    Args:
        dashboard_id: The ID of the dashboard to toggle
        request: The FastAPI request object containing the authenticated user
        service: The dashboard favorite service (injected)

    Returns:
        DashboardFavoriteToggleResponse with the updated favorite status
    """
    return service.toggle_favorite(current_user.id, dashboard_id)


@router.get("/favorites", response_model=DashboardFavoriteListResponse)
@inject
async def get_user_favorites(
    find: DashboardFavoriteFind = Depends(),
    current_user: dict = Depends(get_current_user),
    service: DashboardFavoriteService = Depends(
        Provide[Container.dashboard_favorite_service]
    ),
) -> DashboardFavoriteListResponse:
    return service.get_user_favorites(current_user.id, find)
