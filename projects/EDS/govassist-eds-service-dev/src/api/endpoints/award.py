from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.award_schema import AwardFind, AwardInfo, AwardListResponse
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.services.award_service import AwardService

router = APIRouter(prefix="/awards", tags=["Awards"])


@router.get("", response_model=AwardListResponse)
@inject
def get_awards(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: AwardFind = Depends(),
    service: AwardService = Depends(Provide[Container.award_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=AwardInfo)
@inject
def get_award(
    id: int,
    service: AwardService = Depends(Provide[Container.award_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: AwardService = Depends(Provide[Container.award_service]),
):
    return service.get_unique_values(find_query)
