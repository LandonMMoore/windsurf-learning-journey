from fastapi import APIRouter, Depends

from src.api.endpoints.additional_fund import router as additional_fund_router
from src.api.endpoints.ai_assistant import router as ai_assistant_router
from src.api.endpoints.award import router as award_router
from src.api.endpoints.budget_info import router as budget_info_router
from src.api.endpoints.budget_items import router as budget_items_router
from src.api.endpoints.cost_center import router as cost_center_router
from src.api.endpoints.dashboard import router as dashboard_router
from src.api.endpoints.dashboard_favorite import router as dashboard_favorite_router
from src.api.endpoints.dashboard_widget import router as dashboard_widget_router
from src.api.endpoints.federal_fund import router as federal_fund_router
from src.api.endpoints.feedback_par import router as feedback_par_router
from src.api.endpoints.fhwa import router as fhwa_router
from src.api.endpoints.fhwa_award_type import router as fhwa_award_type_router
from src.api.endpoints.filter_configurations import (
    router as filter_configurations_router,
)
from src.api.endpoints.filter_definitions import router as filter_definitions_router
from src.api.endpoints.fund import router as fund_router
from src.api.endpoints.health import router as health_router
from src.api.endpoints.integration import router as integration_router
from src.api.endpoints.integration import webhook_router as integration_webhook_router
from src.api.endpoints.key_metrics import router as key_metrics_router
from src.api.endpoints.master_project import router as master_project_router
from src.api.endpoints.organization import router as organization_router
from src.api.endpoints.par import router as par_router
from src.api.endpoints.par_activity import router as par_activity_router
from src.api.endpoints.par_award_association import (
    router as par_award_association_router,
)
from src.api.endpoints.par_budget_analysis import router as par_budget_analysis_router
from src.api.endpoints.par_meta import router as par_meta_router
from src.api.endpoints.par_state_api import router as par_state_api_router
from src.api.endpoints.preconfigured_widget import router as preconfigured_widget_router
from src.api.endpoints.project_detail import router as project_detail_router
from src.api.endpoints.project_location import router as project_location_router
from src.api.endpoints.report_generation import router as report_generation_router
from src.api.endpoints.reports import router as reports_router
from src.api.endpoints.sub_report import router as sub_report_router
from src.api.endpoints.widget_favorite import router as widget_favorite_router
from src.api.endpoints.widgets_config import router as widgets_config_router
from src.api.endpoints.workflow import router as workflow_router
from src.api.endpoints.workflow_status import router as workflow_status_router
from src.core.dependencies import require_auth

# Public routes (no authentication required)
routers = APIRouter()
router_list = [health_router, integration_webhook_router]

for router in router_list:
    routers.include_router(router)

# Private routes (authentication required)
private_routers = APIRouter(dependencies=[Depends(require_auth())])
private_router_list = [
    widget_favorite_router,
    dashboard_widget_router,
    dashboard_router,
    dashboard_favorite_router,
    award_router,
    cost_center_router,
    federal_fund_router,
    fhwa_router,
    fund_router,
    master_project_router,
    fhwa_award_type_router,
    project_location_router,
    par_award_association_router,
    project_detail_router,
    organization_router,
    par_router,
    budget_info_router,
    budget_items_router,
    par_activity_router,
    feedback_par_router,
    par_meta_router,
    key_metrics_router,
    additional_fund_router,
    par_budget_analysis_router,
    preconfigured_widget_router,
    filter_definitions_router,
    widgets_config_router,
    ai_assistant_router,
    report_generation_router,
    reports_router,
    filter_configurations_router,
    workflow_status_router,
    workflow_router,
    par_state_api_router,
    integration_router,
    sub_report_router,
]

for router in private_router_list:
    private_routers.include_router(router)
