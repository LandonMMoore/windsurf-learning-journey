from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.budget_analysis_fund_schema import (
    BudgetAnalysisFundDelete,
    BudgetAnalysisFundInfo,
    BudgetAnalysisFundRequest,
    BudgetAnalysisFundUpdate,
)
from src.services.budget_analysis_fund_service import BudgetAnalysisFundService

router = APIRouter(prefix="/budget-analysis-funds", tags=["Budget Analysis Funds"])


@router.post("", response_model=dict)
@inject
def create_budget_analysis_fund(
    request_data: BudgetAnalysisFundRequest,
    service: BudgetAnalysisFundService = Depends(
        Provide[Container.budget_analysis_fund_service]
    ),
):
    return service.create_budget_analysis_fund(request_data)


@router.get("/get-by-par-id/{par_id}")
@inject
def get_budget_analysis_fund(
    par_id: int,
    service: BudgetAnalysisFundService = Depends(
        Provide[Container.budget_analysis_fund_service]
    ),
):
    return service.get_budget_analysis_fund(par_id)


@router.patch("/{id}", response_model=BudgetAnalysisFundInfo)
@inject
def update_budget_analysis_fund(
    id: int,
    data: BudgetAnalysisFundUpdate,
    service: BudgetAnalysisFundService = Depends(
        Provide[Container.budget_analysis_fund_service]
    ),
):
    return service.patch(id, data)


@router.delete("/{id}", response_model=dict)
@inject
def delete_budget_analysis_fund(
    data: BudgetAnalysisFundDelete,
    service: BudgetAnalysisFundService = Depends(
        Provide[Container.budget_analysis_fund_service]
    ),
):
    return service.delete_budget_analysis_fund(data)
