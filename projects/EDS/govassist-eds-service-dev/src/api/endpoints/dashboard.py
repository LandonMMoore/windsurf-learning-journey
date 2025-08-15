from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.core.dependencies import get_current_user
from src.core.exception_handlers import InternalServerError
from src.core.exceptions import NotFoundError, UnauthorizedError
from src.schema.dashboard_schema import (
    DashboardCreate,
    DashboardFilterConfigResponse,
    DashboardFilterIndexType,
    DashboardFiltersUpdate,
    DashboardFind,
    DashboardInfo,
    DashboardListResponse,
    DashboardShareListResponse,
    DashboardShareRequest,
    DashboardUpdate,
    RecentDashboardsResponse,
)
from src.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get("", response_model=DashboardListResponse)
@inject
def get_dashboards(
    find: DashboardFind = Depends(),
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    return service.get_dashboards(current_user.id, find)


@router.get("/recent", response_model=RecentDashboardsResponse)
@inject
def get_recent_dashboards(
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    return service.get_recent_dashboards(current_user.id)


@router.get("/filter-config", response_model=DashboardFilterConfigResponse)
@inject
async def get_dashboard_filter_config(
    index: DashboardFilterIndexType = Depends(),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
) -> DashboardFilterConfigResponse:
    """
    Get fields for dashboard filtering with supported filter types

    Args:
        index_type: Type of fields to return
            - 'common': Fields available across all indices (universal fields)
            - 'r085_v3': Fields specific to R085_v3 index
            - 'r025': Fields specific to R025 index

    Returns:
        DashboardFilterConfigResponse containing fields with their supported filter types
    """
    try:
        # Delegate to service layer - service already returns the correct structure
        result = await service.get_filter_configuration(index.index_type)
        return result
    except Exception:
        raise InternalServerError(
            detail=f"Error fetching fields for {index.index_type}"
        )


@router.get("/{id}", response_model=DashboardInfo)
@inject
def get_dashboard(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    # Check if user has access to this dashboard
    return service.get_dashboard(id, current_user.id)


@router.post("", response_model=DashboardInfo)
@inject
def create_dashboard(
    dashboard: DashboardCreate,
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    return service.add(dashboard, current_user.id)


@router.patch("/{id}", response_model=DashboardInfo)
@inject
def update_dashboard(
    id: int,
    dashboard: DashboardUpdate,
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    return service.patch(id, dashboard)


@router.delete("/bulk", response_model=dict)
@inject
def bulk_delete_dashboard(
    ids: List[int],
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    return service.bulk_dashboard_delete(ids, current_user.id)


@router.delete("/{id}", response_model=dict)
@inject
def delete_dashboard(
    id: int,
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    service.remove_by_id(id)
    return {"message": "Dashboard deleted successfully"}


@router.post("/clone", response_model=DashboardInfo)
@inject
def clone_dashboard(
    dashboard_id: int,
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    return service.clone_dashboard(dashboard_id, current_user.id)


@router.post("/{id}/share", response_model=DashboardInfo)
@inject
def share_dashboard(
    id: int,
    share_request: DashboardShareRequest,
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    """
    Share a dashboard with other users or change its visibility.

    Parameters:
    - id: The ID of the dashboard to share
    - share_request: The request body containing share type and users to add/remove
    """
    return service.shared_dashboard(
        dashboard_id=id,
        user_id=current_user.id,
        share_type=share_request.share_type,
        add_share_with=share_request.add_share_with,
        remove_share_with=share_request.remove_share_with,
    )


@router.get("/dashboard-share-list/{id}", response_model=DashboardShareListResponse)
@inject
def get_dashboard_share_list(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
):
    """
    Get the share list for a specific dashboard.

    Args:
        id: The ID of the dashboard
        current_user: Current authenticated user
        service: Dashboard service

    Returns:
        DashboardShareListResponse containing visibility and shared users
    """
    return service.get_dashboard_share_list(id, current_user.id)


@router.patch(
    "/{dashboard_id}/save-filter", response_model=DashboardFilterConfigResponse
)
@inject
def save_dashboard_filters(
    filters_update: DashboardFiltersUpdate,
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(Provide[Container.dashboard_service]),
) -> DashboardFilterConfigResponse:
    try:
        result = service.save_dashboard_filters(
            dashboard_id=filters_update.dashboard_id,
            filters=filters_update.filters,
            user_id=current_user.id,
        )
        return DashboardFilterConfigResponse(
            success=True, data=result, message="Dashboard filters saved successfully"
        )

    except (UnauthorizedError, NotFoundError):
        raise
    except Exception:
        raise InternalServerError(detail="Error saving dashboard filters")
