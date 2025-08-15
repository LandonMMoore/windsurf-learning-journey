from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class FhwaBase(BaseModel):
    program_code: Optional[str] = None
    project_number: Optional[str] = None
    soar_grant: Optional[str] = None
    soar_project_no: Optional[str] = None
    stip_reference: Optional[str] = None
    categories: Optional[str] = None


class FhwaCreate(FhwaBase):
    pass


class FhwaUpdate(FhwaBase):
    pass


class FhwaFind(make_optional(FindBase), make_optional(FhwaBase)):
    pass


class FhwaInfo(ModelBaseInfo, FhwaBase):
    pass


class FhwaListResponse(FindResult):
    founds: Optional[List[FhwaInfo]] = None
    search_options: Optional[SearchOptions] = None


class FhwaProgramCodeInfo(BaseModel):
    program_code: Optional[str] = None
    id: Optional[int] = None


class FhwaProjectNumberInfo(BaseModel):
    project_number: Optional[str] = None
    id: Optional[int] = None


class FhwaSoarGrantInfo(BaseModel):
    soar_grant: Optional[str] = None
    id: Optional[int] = None


class FhwaSoarProjectNoInfo(BaseModel):
    soar_project_no: Optional[str] = None
    id: Optional[int] = None


class FhwaStipReferenceInfo(BaseModel):
    stip_reference: Optional[str] = None
    id: Optional[int] = None


class FhwaCategoriesInfo(BaseModel):
    categories: Optional[str] = None
    id: Optional[int] = None
