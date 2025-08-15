from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class ProjectLocationBase(BaseModel):
    location: Optional[str] = None


class ProjectLocationCreate(ProjectLocationBase):
    pass


class ProjectLocationUpdate(ProjectLocationBase):
    pass


class ProjectLocationFind(make_optional(FindBase), make_optional(ProjectLocationBase)):
    pass


class ProjectLocationInfo(ModelBaseInfo, ProjectLocationBase):
    pass


class ProjectLocationListResponse(FindResult):
    founds: Optional[List[ProjectLocationInfo]] = None
    search_options: Optional[SearchOptions] = None
