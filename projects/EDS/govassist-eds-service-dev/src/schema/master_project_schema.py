from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class MasterProjectBase(BaseModel):
    master_project_number: Optional[int] = None
    master_project_name: Optional[str] = None


class MasterProjectCreate(MasterProjectBase):
    pass


class MasterProjectUpdate(MasterProjectBase):
    pass


class MasterProjectFind(make_optional(FindBase), make_optional(MasterProjectBase)):
    pass


class MasterProjectInfo(ModelBaseInfo, MasterProjectBase):
    pass


class MasterProjectListResponse(FindResult):
    founds: Optional[List[MasterProjectInfo]] = None
    search_options: Optional[SearchOptions] = None
