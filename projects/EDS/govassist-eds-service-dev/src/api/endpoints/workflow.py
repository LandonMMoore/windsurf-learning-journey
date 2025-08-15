from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.workflow_schema import WorkflowFind, WorkflowInfo, WorkflowListResponse
from src.services.workflow_crud_service import WorkflowCrudService

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=WorkflowListResponse)
@inject
def get_workflows(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: WorkflowFind = Depends(),
    service: WorkflowCrudService = Depends(Provide[Container.workflow_crud_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=WorkflowInfo)
@inject
def get_workflow(
    id: int,
    service: WorkflowCrudService = Depends(Provide[Container.workflow_crud_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: WorkflowCrudService = Depends(Provide[Container.workflow_crud_service]),
):
    return service.get_unique_values(find_query)
