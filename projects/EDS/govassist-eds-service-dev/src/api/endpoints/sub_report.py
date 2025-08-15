from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.report_schema import (
    SubReportCreate,
    SubReportInfo,
    SubReportUpdate,
    ValidateFormula,
)
from src.services.sub_report_service import SubReportService

router = APIRouter(prefix="/sub-reports", tags=["Sub Reports"])


@router.post("", response_model=SubReportInfo)
@inject
def create_sub_report(
    sub_report: SubReportCreate,
    service: SubReportService = Depends(Provide[Container.sub_report_service]),
):
    """Create a new sub-report configuration"""
    return service.add(sub_report)


@router.patch("/{sub_report_id}", response_model=SubReportInfo)
@inject
def update_sub_report(
    sub_report_id: int,
    sub_report: SubReportUpdate,
    service: SubReportService = Depends(Provide[Container.sub_report_service]),
):
    """Update a sub-report configuration"""
    return service.patch(
        sub_report_id, sub_report, exclude_none=False, exclude_unset=True
    )


@router.post("/validate-formula")
@inject
def validate_formula(
    formula: ValidateFormula,
    service: SubReportService = Depends(Provide[Container.sub_report_service]),
):
    return service.validate_formula(formula.formula)


@router.get(
    "/sub-report-workflow-details/{report_configuration_id}",
    response_model=List[Dict[str, Any]],
)
@inject
def get_sub_report_workflow_details(
    report_configuration_id: int,
    service: SubReportService = Depends(Provide[Container.sub_report_service]),
):
    return service.get_sub_report_workflow_details(report_configuration_id)


@router.delete("/{sub_report_id}")
@inject
def delete_sub_report(
    sub_report_id: int,
    service: SubReportService = Depends(Provide[Container.sub_report_service]),
):
    """Delete a sub-report configuration"""
    service.remove_by_id(sub_report_id)
    return {"message": "Sub-report configuration deleted successfully"}


@router.post("/{sub_report_id}/publish")
@inject
def publish_sub_report(
    sub_report_id: int,
    service: SubReportService = Depends(Provide[Container.sub_report_service]),
):
    return service.publish_sub_report(sub_report_id)
