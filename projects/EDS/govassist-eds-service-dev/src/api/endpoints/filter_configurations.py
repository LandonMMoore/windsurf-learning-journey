from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.core.dependencies import get_current_user
from src.schema.par_dashboard_filter_configurations_schema import (
    ParDashboardFilterConfigurationsCreate,
    ParDashboardFilterConfigurationsFind,
    ParDashboardFilterConfigurationsInfo,
    ParDashboardFilterConfigurationsListResponse,
    ParDashboardFilterConfigurationsUpdate,
)
from src.services.par_dashboard_filter_configurations_service import (
    ParDashboardFilterConfigurationsService,
)

router = APIRouter(prefix="/filter-configurations", tags=["Filter Configurations"])


@router.get("", response_model=ParDashboardFilterConfigurationsListResponse)
@inject
def get_filter_configurations(
    searchable_fields: Optional[List[str]] = Query(default=None),
    find: ParDashboardFilterConfigurationsFind = Depends(),
    current_user: dict = Depends(get_current_user),
    service: ParDashboardFilterConfigurationsService = Depends(
        Provide[Container.par_dashboard_filter_configurations_service]
    ),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=ParDashboardFilterConfigurationsInfo)
@inject
def get_filter_configuration_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: ParDashboardFilterConfigurationsService = Depends(
        Provide[Container.par_dashboard_filter_configurations_service]
    ),
):
    return service.get_by_id(id)


@router.post("", response_model=ParDashboardFilterConfigurationsInfo)
@inject
def create_filter_configuration(
    filter_config: ParDashboardFilterConfigurationsCreate,
    current_user: dict = Depends(get_current_user),
    service: ParDashboardFilterConfigurationsService = Depends(
        Provide[Container.par_dashboard_filter_configurations_service]
    ),
):
    return service.add(filter_config)


@router.patch("/{id}", response_model=ParDashboardFilterConfigurationsInfo)
@inject
def update_filter_configuration_by_id(
    id: int,
    filter_config: ParDashboardFilterConfigurationsUpdate,
    current_user: dict = Depends(get_current_user),
    service: ParDashboardFilterConfigurationsService = Depends(
        Provide[Container.par_dashboard_filter_configurations_service]
    ),
):
    return service.patch(id, filter_config)


@router.delete("/{id}", response_model=dict)
@inject
def delete_filter_configuration_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: ParDashboardFilterConfigurationsService = Depends(
        Provide[Container.par_dashboard_filter_configurations_service]
    ),
):
    service.remove_by_id(id)
    return {"message": "Filter configuration deleted successfully"}
