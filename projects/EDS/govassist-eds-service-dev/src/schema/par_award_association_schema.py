from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import FindBase, FindResult, SearchOptions, make_optional


class ParAwardAssociationBase(BaseModel):
    project_details_id: Optional[int] = None
    award_type_id: Optional[int] = None


class ParAwardAssociationCreate(ParAwardAssociationBase):
    pass


class ParAwardAssociationUpdate(ParAwardAssociationBase):
    pass


class ParAwardAssociationFind(
    make_optional(FindBase), make_optional(ParAwardAssociationBase)
):
    pass


class AwardTypeInfo(BaseModel):
    id: int
    code: str
    description: str


class ParAwardAssociationInfo(BaseModel):
    id: int
    project_details_id: Optional[int] = None
    award_type_id: Optional[int] = None
    award_type: Optional[AwardTypeInfo] = None


class ParAwardAssociationListResponse(FindResult):
    founds: Optional[List[ParAwardAssociationInfo]] = None
    search_options: Optional[SearchOptions] = None
