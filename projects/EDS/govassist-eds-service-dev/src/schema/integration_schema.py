from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.schema.base_schema import FindBase, make_optional


class ActiveIntegration(BaseModel):
    id: int
    uuid: str
    user_id: int
    name: str
    email: Optional[str] = None
    folder_id: str
    folder_name: str
    integration_id: str
    integration_uuid: str
    site_id: str
    list_id: str
    drive_id: str
    path: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ActiveIntegrationResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[ActiveIntegration] = None


class IntegrationBase(BaseModel):
    user_id: int
    integration_id: str
    folder_id: str
    folder_name: str
    site_id: str
    drive_id: str
    path: str
    list_id: str
    webhook_info: dict = {}
    is_active: bool = True


class IntegrationCreate(IntegrationBase):
    pass


class IntegrationUpdate(make_optional(IntegrationBase)):
    pass


class IntegrationFind(make_optional(FindBase), make_optional(IntegrationBase)):
    pass


class SubscribeDirectory(BaseModel):
    integration_id: str
    integration_uuid: str
    folder_id: str
    folder_name: str
    site_id: str
    list_id: str
    drive_id: str
    path: str
    resource: str

    class Config:
        populate_by_name = True


# Response Schemas for Industrial Standards
class SubscriptionSuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class SharepointSubscription(BaseModel):
    changeType: str
    clientState: str
    notificationUrl: str
    resource: str
    expirationDateTime: datetime


class GetFolderStructureQuery(BaseModel):
    integration_id: str
    site_id: str
    list_id: str
    path: Optional[str] = None


class SharepointSite(BaseModel):
    id: str
    name: str
    display_name: str


class SharepointFolder(BaseModel):
    id: str
    name: str
    path: str
    has_children: bool
    drive_id: str


class SharepointFile(BaseModel):
    id: str
    name: str
    size: int
    url: Optional[str] = None
    type: Optional[str] = None
    last_modified: Optional[str] = None
    drive_id: str


class SharepointFolderList(BaseModel):
    folders: List[SharepointFolder]
    files: List[SharepointFile]
    current_path: str


class SharepointIntegration(BaseModel):
    id: Optional[str] = None
    uuid: Optional[str] = None
    user_id: Optional[int] = None
    email: Optional[str] = None
    provider_name: Optional[str] = None


class SharepointSiteLists(BaseModel):
    id: str
    name: str
    display_name: str
    created_datetime: str
    last_modified_dateTime: str
    template: str
