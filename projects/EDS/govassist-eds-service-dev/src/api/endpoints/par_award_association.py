from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.par_award_association_schema import (
    ParAwardAssociationCreate,
    ParAwardAssociationFind,
    ParAwardAssociationInfo,
    ParAwardAssociationListResponse,
    ParAwardAssociationUpdate,
)
from src.services.par_award_association_service import ParAwardAssociationService

router = APIRouter(prefix="/par-award-associations", tags=["PAR Award Associations"])


@router.post("", response_model=ParAwardAssociationInfo)
@inject
def create_par_award_association(
    data: ParAwardAssociationCreate,
    service: ParAwardAssociationService = Depends(
        Provide[Container.par_award_association_service]
    ),
):
    return service.add(data)


@router.get("", response_model=ParAwardAssociationListResponse)
@inject
def get_par_award_associations(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: ParAwardAssociationFind = Depends(),
    service: ParAwardAssociationService = Depends(
        Provide[Container.par_award_association_service]
    ),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=ParAwardAssociationInfo)
@inject
def get_par_award_association(
    id: int,
    service: ParAwardAssociationService = Depends(
        Provide[Container.par_award_association_service]
    ),
):
    return service.get_by_id(id)


@router.patch("/{id}", response_model=ParAwardAssociationInfo)
@inject
def update_par_award_association(
    id: int,
    data: ParAwardAssociationUpdate,
    service: ParAwardAssociationService = Depends(
        Provide[Container.par_award_association_service]
    ),
):
    return service.patch(id, data)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: ParAwardAssociationService = Depends(
        Provide[Container.par_award_association_service]
    ),
):
    return service.get_unique_values(find_query)


@router.put(
    "/difs/{project_details_id}", response_model=ParAwardAssociationListResponse
)
@inject
async def update_by_project_details_id(
    project_details_id: int,
    award_type_ids: List[int],
    service: ParAwardAssociationService = Depends(
        Provide[Container.par_award_association_service]
    ),
):

    return await service.update_by_project_details_id(
        project_details_id, award_type_ids
    )
