from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.project_detail_schema import (
    ProjectDetailCreateRequest,
    ProjectDetailCreateResponse,
    ProjectDetailFind,
    ProjectDetailInfo,
    ProjectDetailListResponse,
    ProjectDetailUpdate,
)
from src.services.project_detail_service import ProjectDetailService

router = APIRouter(prefix="/project-details", tags=["Project Details"])


@router.get("", response_model=ProjectDetailListResponse)
@inject
def get_project_details(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: ProjectDetailFind = Depends(),
    service: ProjectDetailService = Depends(Provide[Container.project_detail_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/get-difs-project-name-list")
@inject
def difs_project_name_list(
    service: ProjectDetailService = Depends(Provide[Container.project_detail_service]),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(15, description="Page size", ge=1, le=100),
    request_type: Optional[str] = Query(None, description="Request type"),
    search: Optional[str] = Query(
        None, description="Search term for project number or project name"
    ),
):
    return service.sync_project_name_with_project_number(
        page=page, page_size=page_size, search=search, request_type=request_type
    )


@router.get("/{id}", response_model=ProjectDetailInfo)
@inject
def get_project_detail(
    id: int,
    service: ProjectDetailService = Depends(Provide[Container.project_detail_service]),
):
    return service.get_by_id(id)


@router.post("", response_model=ProjectDetailCreateResponse)
@inject
async def create_project_detail(
    project_detail: ProjectDetailCreateRequest,
    service: ProjectDetailService = Depends(Provide[Container.project_detail_service]),
):
    return await service.add(project_detail)


@router.patch("/{id}", response_model=ProjectDetailUpdate)
@inject
async def update_project_detail(
    id: int,
    project_detail: ProjectDetailUpdate,
    service: ProjectDetailService = Depends(Provide[Container.project_detail_service]),
):
    return await service.patch(id, project_detail)
