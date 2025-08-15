from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.workflow_status_schema import (
    WorkflowStatusFind,
    WorkflowStatusListResponse,
)
from src.services.workflow_status_service import WorkflowStatusService

router = APIRouter(prefix="/workflow-statuses", tags=["Workflow Statuses"])


@router.get("", response_model=WorkflowStatusListResponse)
@inject
def get_workflow_statuses(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    service: WorkflowStatusService = Depends(
        Provide[Container.workflow_status_service]
    ),
):
    find = WorkflowStatusFind()
    return service.get_list(find, searchable_fields)


# @router.get("/{id}", response_model=WorkflowStatusInfo)
# @inject
# def get_workflow_status(
#     id: int,
#     service: WorkflowStatusService = Depends(
#         Provide[Container.workflow_status_service]
#     ),
# ):
#     return service.get_by_id(id)


# @router.post("/", response_model=WorkflowStatusInfo)
# @inject
# def add_workflow_status(
#     workflow_status: WorkflowStatusCreate,
#     service: WorkflowStatusService = Depends(
#         Provide[Container.workflow_status_service]
#     ),
# ):
#     return service.add(workflow_status)
