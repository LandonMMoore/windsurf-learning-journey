from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.fund_schema import FundFind, FundInfo, FundListResponse
from src.services.fund_service import FundService

router = APIRouter(prefix="/funds", tags=["Funds"])


@router.get("", response_model=FundListResponse)
@inject
def get_funds(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: FundFind = Depends(),
    service: FundService = Depends(Provide[Container.fund_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=FundInfo)
@inject
def get_fund(
    id: int,
    service: FundService = Depends(Provide[Container.fund_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: FundService = Depends(Provide[Container.fund_service]),
):
    return service.get_unique_values(find_query)
