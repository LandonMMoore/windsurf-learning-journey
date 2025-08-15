from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.federal_fund_schema import (
    FederalFundFind,
    FederalFundInfo,
    FederalFundListResponse,
)
from src.services.federal_fund_service import FederalFundService

router = APIRouter(prefix="/federal-funds", tags=["Federal Funds"])


@router.get("/", response_model=FederalFundListResponse)
@inject
def get_federal_funds(
    find: FederalFundFind = Depends(),
    exclude_fund_id: Optional[List[int]] = Query(None),
    service: FederalFundService = Depends(Provide[Container.federal_fund_service]),
):
    return service.get_list(find, exclude_fund_id)


@router.get("/{id}", response_model=FederalFundInfo)
@inject
def get_federal_fund(
    id: int,
    service: FederalFundService = Depends(Provide[Container.federal_fund_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: FederalFundService = Depends(Provide[Container.federal_fund_service]),
):
    return service.get_unique_values(find_query)
