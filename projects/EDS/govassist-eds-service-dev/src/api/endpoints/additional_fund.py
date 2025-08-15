from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.additional_fund_schema import AdditionalFundBase, AdditionalFundInfo
from src.services.additional_fund_service import AdditionalFundService

router = APIRouter(prefix="/additional-fund", tags=["Additional Fund"])


@router.post("", response_model=AdditionalFundInfo)
@inject
def create_additional_fund(
    data: AdditionalFundBase,
    service: AdditionalFundService = Depends(
        Provide[Container.additional_fund_service]
    ),
):
    return service.add(data)


@router.patch("/{id}", response_model=AdditionalFundInfo)
@inject
def update_additional_fund(
    id: int,
    data: AdditionalFundBase,
    service: AdditionalFundService = Depends(
        Provide[Container.additional_fund_service]
    ),
):
    return service.patch(id, data)


@router.delete("/{id}", response_model=str)
@inject
def delete_additional_fund(
    id: int,
    service: AdditionalFundService = Depends(
        Provide[Container.additional_fund_service]
    ),
):
    service.remove_by_id(id)
    return "Additional fund deleted successfully"


@router.get("/{budget_analysis_id}")
@inject
def get_additional_fund_by_par_budget_analysis_id(
    budget_analysis_id: int,
    service: AdditionalFundService = Depends(
        Provide[Container.additional_fund_service]
    ),
):
    return service.get_by_budget_analysis_id(budget_analysis_id)
