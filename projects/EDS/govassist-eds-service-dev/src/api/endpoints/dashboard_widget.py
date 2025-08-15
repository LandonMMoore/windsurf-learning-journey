from typing import Any, Dict, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request

from src.api import limiter
from src.core.container import Container
from src.core.dependencies import get_current_user
from src.core.middleware import inject as custom_inject
from src.elasticsearch.group_by import build_aggregation_query
from src.schema.dashboard_widget_schema import (
    DashboardWidgetBulkUpdate,
    DashboardWidgetCreate,
    DashboardWidgetFind,
    DashboardWidgetInfo,
    DashboardWidgetListResponse,
    DashboardWidgetUpdate,
    FetchedData,
)
from src.schema.preconfigured_widget_schema import (
    PreconfiguredWidgetInfo,
    PreconfiguredWidgetSave,
)
from src.services.dashboard_widget_service import DashboardWidgetService

router = APIRouter(prefix="/dashboard-widgets", tags=["Dashboard Widgets"])


@router.get("", response_model=DashboardWidgetListResponse)
@inject
def get_dashboard_widgets(
    find: DashboardWidgetFind = Depends(),
    current_user: dict = Depends(get_current_user),
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Get list of dashboard widgets with favorite status for the current user."""
    return service.get_widget_list(find, current_user.id)


@router.post("/fetch-data", response_model=dict)
@custom_inject
@limiter.limit("50/minute")
async def get_dashboard_widget_data(
    request: Request, data: FetchedData, dashboard_id: int = None
):
    """Fetch widget data with optional global filter integration"""
    return await build_aggregation_query(data, dashboard_id)


@router.post("/bulk-update", response_model=List[DashboardWidgetInfo])
@inject
def bulk_update_dashboard_widget(
    data: DashboardWidgetBulkUpdate,
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Bulk update dashboard widgets."""
    return service.bulk_update(data)


@router.post("/clone-widget", response_model=DashboardWidgetInfo)
@inject
def clone_widget(
    widget_id: int,
    dashboard_id: int,
    current_user: dict = Depends(get_current_user),
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Clone a dashboard widget to a specified dashboard."""
    data = service.get_widget_by_id(widget_id, current_user.id)
    return service.clone_widget(data, dashboard_id)


@router.post("/save-as-preconfigured-widget", response_model=PreconfiguredWidgetInfo)
@inject
def save_dashboard_widget_as_preconfigured_widget(
    preconfigured_widget: PreconfiguredWidgetSave,
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Save a dashboard widget as a preconfigured widget."""
    return service.save_dashboard_widget_as_preconfigured_widget(preconfigured_widget)


@router.post("/{id}")
@custom_inject
@limiter.limit("50/minute")
async def dashboard_widget_data(
    request: Request,
    id: int,
    current_user: dict = Depends(get_current_user),
    filter: Optional[Dict[str, Any]] = Body(default=None),
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Fetch dashboard widget data with optional global filter integration."""
    data = service.get_widget_by_id(id, current_user.id)
    # Extract dashboard_id from the widget data for global filter integration
    dashboard_id = getattr(data, "dashboard_id", None)
    data.config["filters"] = data.filters
    # Create FetchedData object directly from widget data
    widget_data = FetchedData(
        widget_type=data.widget_type,
        config=data.config or {},
        data_source=data.data_source,
    )

    # Build the aggregation query
    result = await build_aggregation_query(widget_data, dashboard_id, filter)

    # Add dashboard_id to the widget_data for filter integration
    widget_data_dict = widget_data.dict()
    widget_data_dict["dashboard_id"] = dashboard_id
    widget_data_dict["name"] = data.name

    # build_aggregation_query always returns {"widget_data": ..., "data": ...}
    # If result is None or has no data, return None for data
    actual_data = result.get("data") if result else None

    return {"widget_data": widget_data_dict, "data": actual_data}


@router.post("", response_model=DashboardWidgetInfo)
@inject
def create_dashboard_widget(
    dashboard_widget: DashboardWidgetCreate,
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Create a new dashboard widget."""
    return service.add(dashboard_widget)


@router.patch("/{id}", response_model=DashboardWidgetInfo)
@inject
def update_dashboard_widget(
    id: int,
    dashboard_widget: DashboardWidgetUpdate,
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Update a dashboard widget."""
    return service.patch(id, dashboard_widget)


@router.delete("/{id}")
@inject
def delete_dashboard_widget(
    id: int,
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Delete a dashboard widget."""
    service.remove_by_id(id)
    return {"message": "Dashboard widget deleted successfully"}


@router.delete("/preconfigured-widget/{id}")
@inject
def delete_preconfigured_widget(
    id: int,
    service: DashboardWidgetService = Depends(
        Provide[Container.dashboard_widget_service]
    ),
):
    """Delete a preconfigured widget."""
    return service.delete_preconfigured_widget(id)
