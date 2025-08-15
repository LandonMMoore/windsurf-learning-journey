from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.budget_items_schema import (
    BudgetItemsCreate,
    BudgetItemsFind,
    BudgetItemsInfo,
    BudgetItemsListResponse,
    BudgetItemsUpdate,
)
from src.services.budget_items_service import BudgetItemsService

router = APIRouter(prefix="/budget-items", tags=["Budget Items"])


@router.get("", response_model=BudgetItemsListResponse)
@inject
def get_budget_items_list(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: BudgetItemsFind = Depends(),
    service: BudgetItemsService = Depends(Provide[Container.budget_items_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=BudgetItemsInfo)
@inject
def get_budget_item(
    id: int,
    service: BudgetItemsService = Depends(Provide[Container.budget_items_service]),
):
    return service.get_by_id(id)


@router.post("", response_model=BudgetItemsInfo)
@inject
async def create_budget_item(
    data: BudgetItemsCreate,
    service: BudgetItemsService = Depends(Provide[Container.budget_items_service]),
):
    return await service.add(data)


@router.patch("/{id}", response_model=BudgetItemsInfo)
@inject
async def update_budget_item(
    id: int,
    data: BudgetItemsUpdate,
    service: BudgetItemsService = Depends(Provide[Container.budget_items_service]),
):
    return await service.patch(id, data)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: BudgetItemsService = Depends(Provide[Container.budget_items_service]),
):
    return service.get_unique_values(find_query)
