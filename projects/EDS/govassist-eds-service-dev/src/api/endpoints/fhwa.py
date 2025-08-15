from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.fhwa_schema import FhwaFind, FhwaInfo, FhwaListResponse
from src.services.fhwa_service import FhwaService

router = APIRouter(prefix="/fhwa", tags=["FHWA"])


@router.get("/", response_model=FhwaListResponse)
@inject
def get_fhwas(
    find: FhwaFind = Depends(),
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    service: FhwaService = Depends(Provide[Container.fhwa_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=FhwaInfo)
@inject
def get_fhwa(
    id: int,
    service: FhwaService = Depends(Provide[Container.fhwa_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: FhwaService = Depends(Provide[Container.fhwa_service]),
):
    return service.get_unique_values(find_query)


@router.get("/filter-null-values/{field_name}")
@inject
def filter_null_values(
    field_name: str,
    find: FhwaFind = Depends(),
    service: FhwaService = Depends(Provide[Container.fhwa_service]),
):
    return service.filter_null_values(field_name, find)
