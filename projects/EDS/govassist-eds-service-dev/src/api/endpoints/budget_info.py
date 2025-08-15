from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.budget_info_schema import (
    BudgetInfoCreate,
    BudgetInfoFind,
    BudgetInfoInfo,
    BudgetInfoListResponse,
    BudgetInfoUpdate,
)
from src.services.budget_info_service import BudgetInfoService

router = APIRouter(prefix="/budget-info", tags=["Budget Info"])


@router.get("", response_model=BudgetInfoListResponse)
@inject
def get_budget_info_list(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: BudgetInfoFind = Depends(),
    service: BudgetInfoService = Depends(Provide[Container.budget_info_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=BudgetInfoInfo)
@inject
def get_budget_info(
    id: int,
    service: BudgetInfoService = Depends(Provide[Container.budget_info_service]),
):
    return service.get_by_id(id)


@router.post("", response_model=BudgetInfoInfo)
@inject
async def create_budget_info(
    data: BudgetInfoCreate,
    service: BudgetInfoService = Depends(Provide[Container.budget_info_service]),
):
    return await service.add(data)


@router.patch("/{id}", response_model=BudgetInfoInfo)
@inject
async def update_budget_info(
    id: int,
    data: BudgetInfoUpdate,
    service: BudgetInfoService = Depends(Provide[Container.budget_info_service]),
):
    return await service.patch(id, data)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: BudgetInfoService = Depends(Provide[Container.budget_info_service]),
):
    return service.get_unique_values(find_query)
