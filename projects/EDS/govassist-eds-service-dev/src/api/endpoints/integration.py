from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse

from src.core.container import Container
from src.core.dependencies import get_current_user
from src.schema.integration_schema import (
    ActiveIntegrationResponse,
    GetFolderStructureQuery,
    SharepointFolderList,
    SharepointIntegration,
    SharepointSite,
    SharepointSiteLists,
    SubscribeDirectory,
    SubscriptionSuccessResponse,
)
from src.services.integration_service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["Integrations"])
webhook_router = APIRouter(
    prefix="/integrations/webhooks", tags=["Integrations Webhooks"]
)


@router.get("/get-active-subscription", response_model=ActiveIntegrationResponse)
@inject
async def get_active_subscription(
    current_user: dict = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.get_active_subscription(current_user)


@router.get("/get-connections", response_model=List[SharepointIntegration])
@inject
async def get_connections(
    current_user: dict = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.get_connections(current_user)


@router.get("/get-all-sites", response_model=List[SharepointSite])
@inject
async def get_all_sites(
    integration_id: str = Query(..., description="Integration ID"),
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.get_all_sites(integration_id)


@router.get("/get-sites-lists", response_model=List[SharepointSiteLists])
@inject
async def get_sites_lists(
    integration_id: str = Query(..., description="Integration ID"),
    site_id: str = Query(..., description="Site ID"),
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.get_all_lists(integration_id, site_id)


@router.get("/get-folder-list", response_model=SharepointFolderList)
@inject
async def get_folder_list(
    query: GetFolderStructureQuery = Depends(),
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.get_folder_list(
        query.integration_id, query.site_id, query.list_id, query.path
    )


@router.post("/subscribe-directory", response_model=SubscriptionSuccessResponse)
@inject
async def subscribe_directory(
    data: SubscribeDirectory,
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.subscribe_directory(data)


@router.delete("/unsubscribe-all")
@inject
async def unsubscribe_all(
    integration_id: str = Query(..., description="Integration ID"),
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.unsubscribe_all(integration_id)


@router.delete("/delete-subscription")
@inject
async def delete_subscription(
    integration_id: str = Query(..., description="Integration ID"),
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.delete_subscription(integration_id)


@webhook_router.post("/sharepoint")
@inject
async def handle_sharepoint_webhook(
    request: Request,
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    token = request.query_params.get("validationToken")
    if token:
        return PlainTextResponse(content=token, status_code=200)
    return await service.handle_sharepoint_webhook()


@router.get("/test-event-execution")
@inject
async def test_event_execution(
    service: IntegrationService = Depends(Provide[Container.integration_service]),
):
    return await service.handle_sharepoint_webhook()
