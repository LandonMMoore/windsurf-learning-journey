from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.core.dependencies import get_current_user
from src.schema.widget_favorite_schema import (
    WidgetFavoriteFind,
    WidgetFavoriteListResponse,
    WidgetFavoriteToggleResponse,
)
from src.services.widget_favorite_service import WidgetFavoriteService

router = APIRouter(prefix="/widgets", tags=["Widget Favorites"])


@router.post("/{widget_id}/favorite", response_model=WidgetFavoriteToggleResponse)
@inject
async def toggle_widget_favorite(
    widget_id: int,
    current_user: dict = Depends(get_current_user),
    service: WidgetFavoriteService = Depends(
        Provide[Container.widget_favorite_service]
    ),
) -> WidgetFavoriteToggleResponse:
    """
    Toggle favorite status for a widget.

    Args:
        widget_id: The ID of the widget to toggle
        request: The FastAPI request object containing the authenticated user
        service: The widget favorite service (injected)

    Returns:
        WidgetFavoriteToggleResponse with the updated favorite status

    Raises:
        HTTPException: If the widget doesn't exist or user is not authenticated
    """
    return service.toggle_favorite(current_user.id, widget_id)


@router.get("/favorites", response_model=WidgetFavoriteListResponse)
@inject
async def get_user_favorites(
    find: WidgetFavoriteFind = Depends(),
    current_user: dict = Depends(get_current_user),
    service: WidgetFavoriteService = Depends(
        Provide[Container.widget_favorite_service]
    ),
):
    """
    Get all widgets favorited by the current user.

    Args:
        request: The FastAPI request object containing the authenticated user
        find: The find options for pagination and sorting
        service: The widget favorite service (injected)

    Returns:
        WidgetFavoriteListResponse containing the list of favorited widgets and pagination info

    Raises:
        HTTPException: If user is not authenticated
    """
    return service.get_user_favorites(current_user.id, find)
