from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.model.filter_definitions import FilterDefinitionsResponse
from src.services.filter_definitions_service import FilterDefinitionsService

router = APIRouter(prefix="/filter-definitions", tags=["Filter Definitions"])


@router.get("", response_model=FilterDefinitionsResponse)
@inject
def get_filter_definitions(
    service: FilterDefinitionsService = Depends(
        Provide[Container.filter_definitions_service]
    ),
):
    """
    Get metadata about filterable fields for building dynamic filter UI.
    """
    return {"fields": service.get_filter_definitions()}
