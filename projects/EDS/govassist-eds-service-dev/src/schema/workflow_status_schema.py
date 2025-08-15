from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class WorkflowStatusBase(BaseModel):
    state_code: str
    description: Optional[str] = None
    next_state_codes: List[str]
    state_metadata: Optional[dict] = None
    notify_roles: Optional[dict] = None


class WorkflowStatusCreate(WorkflowStatusBase):
    pass


class WorkflowStatusUpdate(make_optional(WorkflowStatusBase)):
    pass


class WorkflowStatusFind(make_optional(FindBase), make_optional(WorkflowStatusBase)):
    pass


class WorkflowStatusInfo(ModelBaseInfo, WorkflowStatusBase):
    pass


class WorkflowStatusListResponse(FindResult):
    founds: Optional[List[WorkflowStatusInfo]] = None
    search_options: Optional[SearchOptions] = None
