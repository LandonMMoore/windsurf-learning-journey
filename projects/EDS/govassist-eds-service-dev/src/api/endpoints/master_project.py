from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.master_project_schema import (
    MasterProjectFind,
    MasterProjectInfo,
    MasterProjectListResponse,
)
from src.services.master_project_service import MasterProjectService

router = APIRouter(prefix="/master-projects", tags=["Master Projects"])


@router.get("", response_model=MasterProjectListResponse)
@inject
def get_master_projects(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: MasterProjectFind = Depends(),
    service: MasterProjectService = Depends(Provide[Container.master_project_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=MasterProjectInfo)
@inject
def get_master_project(
    id: int,
    service: MasterProjectService = Depends(Provide[Container.master_project_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: MasterProjectService = Depends(Provide[Container.master_project_service]),
):
    return service.get_unique_values(find_query)
