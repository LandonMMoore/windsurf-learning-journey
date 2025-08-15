from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.fhwa_award_type_schema import (
    FhwaAwardTypeFind,
    FhwaAwardTypeInfo,
    FhwaAwardTypeListResponse,
)
from src.services.fhwa_award_type_service import FhwaAwardTypeService

router = APIRouter(prefix="/fhwa-award-types", tags=["FHWA Award Types"])


@router.get("", response_model=FhwaAwardTypeListResponse)
@inject
def get_fhwa_award_types(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: FhwaAwardTypeFind = Depends(),
    service: FhwaAwardTypeService = Depends(Provide[Container.fhwa_award_type_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=FhwaAwardTypeInfo)
@inject
def get_fhwa_award_type(
    id: int,
    service: FhwaAwardTypeService = Depends(Provide[Container.fhwa_award_type_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: FhwaAwardTypeService = Depends(Provide[Container.fhwa_award_type_service]),
):
    return service.get_unique_values(find_query)
