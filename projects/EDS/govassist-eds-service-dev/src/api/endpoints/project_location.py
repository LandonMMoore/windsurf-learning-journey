from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.project_location_schema import (
    ProjectLocationFind,
    ProjectLocationInfo,
    ProjectLocationListResponse,
)
from src.services.project_location_service import ProjectLocationService

router = APIRouter(prefix="/project-locations", tags=["Project Locations"])


@router.get("", response_model=ProjectLocationListResponse)
@inject
def get_project_locations(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: ProjectLocationFind = Depends(),
    service: ProjectLocationService = Depends(
        Provide[Container.project_location_service]
    ),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=ProjectLocationInfo)
@inject
def get_project_location(
    id: int,
    service: ProjectLocationService = Depends(
        Provide[Container.project_location_service]
    ),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: ProjectLocationService = Depends(
        Provide[Container.project_location_service]
    ),
):
    return service.get_unique_values(find_query)
