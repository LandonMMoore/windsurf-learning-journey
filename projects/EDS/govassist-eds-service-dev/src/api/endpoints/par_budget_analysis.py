from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.par_budget_analysis_schema import (
    ParBudgetAnalysisInfo,
    ParBudgetAnalysisUpdate,
)
from src.services.budget_analysis_fund_service import BudgetAnalysisFundService
from src.services.par_budget_analysis_service import ParBudgetAnalysisService

router = APIRouter(prefix="/par-budget-analysis", tags=["PAR Budget Analysis"])


@router.patch("/{id}", response_model=ParBudgetAnalysisInfo)
@inject
async def update_par_budget_analysis(
    id: int,
    data: ParBudgetAnalysisUpdate,
    service: ParBudgetAnalysisService = Depends(
        Provide[Container.par_budget_analysis_service]
    ),
):
    return await service.patch(id, data)


@router.get("/par/{par_id}/analyst-data")
@inject
async def get_par_analyst_data(
    par_id: str,
    service: ParBudgetAnalysisService = Depends(
        Provide[Container.par_budget_analysis_service]
    ),
):
    return await service.get_par_analyst_data(par_id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: ParBudgetAnalysisService = Depends(
        Provide[Container.par_budget_analysis_service]
    ),
):
    return service.get_unique_values(find_query)


@router.get("/get-by-par-id/{par_id}")
@inject
def get_budget_analysis_fund(
    par_id: int,
    service: BudgetAnalysisFundService = Depends(
        Provide[Container.budget_analysis_fund_service]
    ),
):
    return service.get_budget_analysis_fund(par_id)
