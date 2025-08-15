from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.cost_center_schema import (
    CostCenterFind,
    CostCenterInfo,
    CostCenterListResponse,
)
from src.services.cost_center_service import CostCenterService

router = APIRouter(prefix="/cost-centers", tags=["Cost Centers"])


@router.get("", response_model=CostCenterListResponse)
@inject
def get_cost_centers(
    find: CostCenterFind = Depends(),
    service: CostCenterService = Depends(Provide[Container.cost_center_service]),
):
    return service.get_list(find)


@router.get("/{id}", response_model=CostCenterInfo)
@inject
def get_cost_center(
    id: int,
    service: CostCenterService = Depends(Provide[Container.cost_center_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: CostCenterService = Depends(Provide[Container.cost_center_service]),
):
    return service.get_unique_values(find_query)
