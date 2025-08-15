from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.elasticsearch.group_by import build_aggregation_query
from src.schema.preconfigured_widget_schema import (
    PreconfiguredWidgetCreate,
    PreconfiguredWidgetFind,
    PreconfiguredWidgetInfo,
    PreconfiguredWidgetListResponse,
    PreconfiguredWidgetUpdate,
)
from src.services.preconfigured_widget_service import PreconfiguredWidgetService

router = APIRouter(prefix="/preconfigured-widgets", tags=["Preconfigured Widgets"])


@router.get("", response_model=PreconfiguredWidgetListResponse)
@inject
def get_preconfigured_widgets(
    find: PreconfiguredWidgetFind = Depends(),
    service: PreconfiguredWidgetService = Depends(
        Provide[Container.preconfigured_widget_service]
    ),
):
    return service.get_list(find)


@router.get("/{id}")
@inject
async def get_preconfigured_widget(
    id: int,
    service: PreconfiguredWidgetService = Depends(
        Provide[Container.preconfigured_widget_service]
    ),
):
    data = service.get_by_id(id)
    return await build_aggregation_query(data)


@router.post("", response_model=PreconfiguredWidgetInfo)
@inject
def create_preconfigured_widget(
    preconfigured_widget: PreconfiguredWidgetCreate,
    service: PreconfiguredWidgetService = Depends(
        Provide[Container.preconfigured_widget_service]
    ),
):
    return service.add(preconfigured_widget)


@router.patch("/{id}", response_model=PreconfiguredWidgetInfo)
@inject
def update_preconfigured_widget(
    id: int,
    preconfigured_widget: PreconfiguredWidgetUpdate,
    service: PreconfiguredWidgetService = Depends(
        Provide[Container.preconfigured_widget_service]
    ),
):
    return service.patch(id, preconfigured_widget)


@router.delete("/{id}", response_model=dict)
@inject
def delete_preconfigured_widget(
    id: int,
    service: PreconfiguredWidgetService = Depends(
        Provide[Container.preconfigured_widget_service]
    ),
):
    service.remove_by_id(id)
    return {"message": "Preconfigured widget deleted successfully"}
