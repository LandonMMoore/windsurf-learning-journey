from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.container import Container
from src.schema.base_schema import FindUniqueValues, UniqueValuesResult
from src.schema.organization_schema import (
    OrganizationFind,
    OrganizationInfo,
    OrganizationListResponse,
)
from src.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("", response_model=OrganizationListResponse)
@inject
def get_organizations(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: OrganizationFind = Depends(),
    service: OrganizationService = Depends(Provide[Container.organization_service]),
):
    return service.get_list(find, searchable_fields)


@router.get("/{id}", response_model=OrganizationInfo)
@inject
def get_organization(
    id: int,
    service: OrganizationService = Depends(Provide[Container.organization_service]),
):
    return service.get_by_id(id)


@router.get("/unique-values/{field_name}", response_model=UniqueValuesResult)
@inject
def get_unique_values(
    find_query: FindUniqueValues = Depends(),
    service: OrganizationService = Depends(Provide[Container.organization_service]),
):
    return service.get_unique_values(find_query)
