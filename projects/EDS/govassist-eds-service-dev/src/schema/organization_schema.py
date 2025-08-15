from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class OrganizationBase(BaseModel):
    project_organization: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationFind(make_optional(FindBase), make_optional(OrganizationBase)):
    pass


class OrganizationInfo(ModelBaseInfo, OrganizationBase):
    pass


class OrganizationListResponse(FindResult):
    founds: Optional[List[OrganizationInfo]] = None
    search_options: Optional[SearchOptions] = None
