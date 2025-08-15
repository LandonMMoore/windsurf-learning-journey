from typing import Annotated, Any, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.core.dependencies import get_current_user
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.par_activity_schema import ParActivityInfo
from src.schema.par_schema import (
    ParCreate,
    ParFind,
    ParInfo,
    ParListResponse,
    ParUpdate,
)
from src.services.par_service import ParService

router = APIRouter(prefix="/pars", tags=["PARs"])


@router.post("", response_model=ParInfo)
@inject
async def create_par(
    data: ParCreate,
    service: ParService = Depends(Provide[Container.par_service]),
):
    return await service.add(data)
    # db_par = service.add(data)
    # par_model = ParModel()
    # es_data = data.dict()
    # es_data["id"] = db_par.id
    # result = par_model.create_par(es_data)
    # return db_par


@router.get("", response_model=ParListResponse)
@inject
def get_pars(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: ParFind = Depends(),
    service: ParService = Depends(Provide[Container.par_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/recent-reviewed", response_model=ParListResponse)
@inject
def get_recently_reviewed_pars(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: ParFind = Depends(),
    current_user: dict = Depends(get_current_user),
    service: ParService = Depends(Provide[Container.par_service]),
):
    """
    Get recently reviewed PARs for the current user with support for searching, filtering, and sorting.

    Args:
        searchable_fields: List of fields to search in (e.g., ['epar_name', 'description'])
        find: Search and filter criteria (same as get_pars endpoint)
        current_user: The authenticated user (injected)
        service: The PAR service (injected)

    Returns:
        Dictionary containing the list of recently reviewed PARs and search options
    """
    return service.get_recently_reviewed_pars(
        str(current_user.id), find, searchable_fields
    )


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: ParService = Depends(Provide[Container.par_service]),
):
    return service.get_unique_values(find_query)


@router.get("/activity/{par_id}", response_model=List[ParActivityInfo])
@inject
def get_par_activity(
    par_id: int,
    service: ParService = Depends(Provide[Container.par_service]),
):
    return service.get_par_activity(par_id)


@router.get("/{id}", response_model=ParFind)
@inject
def get_par(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: ParService = Depends(Provide[Container.par_service]),
):
    """
    Get a PAR by ID and track the view for the current user.

    Args:
        id: The ID of the PAR to retrieve
        current_user: The authenticated user (injected)
        service: The PAR service (injected)

    Returns:
        The PAR data
    """
    # Track the view
    service.track_par_view(str(id), str(current_user.id))
    # Get the PAR data
    return service.get_by_id(id)


@router.patch("/{id}", response_model=ParInfo)
@inject
async def update_par(
    id: int,
    data: ParUpdate,
    service: ParService = Depends(Provide[Container.par_service]),
):
    return await service.patch(id, data)


@router.post("/clone/{par_id}")
@inject
async def clone_par(
    par_id: int,
    request_type: Optional[str] = None,
    service: ParService = Depends(Provide[Container.par_service]),
) -> Any:
    return await service.par_clone(par_id, request_type)


@router.get("/{par_id}/excel")
@inject
async def get_par_excel(
    par_id: int,
    service: ParService = Depends(Provide[Container.par_service]),
):
    return await service.get_par_excel(par_id)
