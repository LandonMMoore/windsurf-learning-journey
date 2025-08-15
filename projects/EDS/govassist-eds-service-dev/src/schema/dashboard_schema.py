from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, constr, validator

from src.core.exception_handlers import ValidationError
from src.model.dashboard_model import VisibilityType
from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)
from src.schema.dashboard_widget_schema import DashboardWidgetInfo

ALPHANUMERIC_PATTERN = r"^[a-zA-Z0-9\s.,\-()&_/;]+$"


class UserInfo(BaseModel):
    name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True


class ShareUser(BaseModel):
    """User to share with."""

    user_id: int = Field(..., description="The ID of the user to share with")
    email: str = Field(..., description="The email of the user to share with")


class DashboardBase(BaseModel):
    """Base dashboard model with required fields."""

    name: str = Field(min_length=1)
    description: Optional[str] = Field(default=None, min_length=2)
    auto_refresh: Optional[bool] = Field(
        default=False,
        description="If true, the dashboard will be refreshed automatically",
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON object containing dashboard filter configurations",
    )

    @validator("filters", pre=True, always=True)
    def validate_filters(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        if not isinstance(v, dict) and not isinstance(v, list):
            raise ValueError("Filters must be a dictionary or list")
        return v


class DashboardCreate(DashboardBase):
    """Schema for creating a new dashboard."""

    name: constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)
    description: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None

    @validator("name", pre=True, always=True)
    def not_empty_or_whitespace(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()

    @validator("description", pre=True, always=True)
    def validate_description(cls, v):
        if v is None:
            return v  # allow None
        if not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()


class DashboardUpdate(make_optional(DashboardBase)):
    """Schema for updating an existing dashboard."""

    name: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    description: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None

    @validator("name", pre=True, always=True)
    def not_empty_or_whitespace(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()

    @validator("description", pre=True, always=True)
    def validate_description(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()


class DashboardFind(make_optional(FindBase)):
    """Schema for searching and filtering dashboards."""

    created_by_me: Optional[bool] = Field(
        default=False,
        description="If true, only dashboards created by the current user will be returned",
    )
    shared_by_me: Optional[bool] = Field(
        default=False,
        description="If true, only dashboards shared by the current user will be returned",
    )
    my_private_dashboards: Optional[bool] = Field(
        default=False,
        description="If true, only dashboards created by the current user will be returned, including PRIVATE ones",
    )
    my_favorites: Optional[bool] = Field(
        default=False,
        description="If true, only dashboards that are in the current user's favorites will be returned",
    )


class DashboardInfo(ModelBaseInfo, DashboardBase):
    """Dashboard information including its widgets with favorite status.

    This class extends the base dashboard information with a list of widgets,
    where each widget includes its favorite status for the current user.
    """

    visibility: VisibilityType = Field(
        default=VisibilityType.PRIVATE,
        description="Visibility type of the dashboard (PUBLIC, PRIVATE, or SHARED)",
    )
    created_by_user: Optional[UserInfo] = Field(
        default=None,
        description="Information about the user who created this dashboard",
    )
    dashboard_widgets: Optional[List[DashboardWidgetInfo]] = Field(
        default=None,
        description="List of widgets in this dashboard, including their favorite status",
    )
    shared_with: Optional[List[ShareUser]] = Field(
        default=None, description="List of users this dashboard is shared with"
    )

    class Config:
        from_attributes = True


class DashboardListResponse(FindResult):
    """Response schema for listing dashboards with search options."""

    # exclude dashboard widgets from dashboard info

    founds: Optional[List[DashboardInfo]] = None
    search_options: Optional[SearchOptions] = None


class ShareType(str, Enum):
    """Enum for the type of sharing."""

    SHARED = "SHARED"
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class DashboardShareRequest(BaseModel):
    """Request body for sharing a dashboard."""

    share_type: ShareType = Field(..., description="The type of sharing")
    add_share_with: Optional[List[ShareUser]] = Field(
        None, description="List of users to share with"
    )
    remove_share_with: Optional[List[ShareUser]] = Field(
        None, description="List of users to remove sharing with"
    )


class RecentDashboards(ModelBaseInfo, DashboardBase):
    """Response schema for recent dashboards."""

    class Config:
        from_attributes = True


class RecentDashboardsResponse(BaseModel):
    recent_created: List[RecentDashboards]
    recent_favorites: List[RecentDashboards]
    recent_created_by: List[RecentDashboards]

    class Config:
        from_attributes = True


class DashboardFiltersUpdate(BaseModel):
    """Schema for updating dashboard filters only."""

    dashboard_id: int
    filters: Dict[str, Any] = Field(
        ..., description="JSON object containing dashboard filter configurations"
    )


class DashboardFilterIndexType(BaseModel):
    index_type: str

    @validator("index_type")
    def validate_index_type(cls, value):
        allowed = ["common", "r085", "r025", "r085_v3"]
        if value in allowed:
            return value
        raise ValidationError(
            f"Invalid index type: {value}. Allowed values: {allowed} or must start with 'custom_'"
        )


class DashboardShareListResponse(BaseModel):
    """Response schema for dashboard share list."""

    visibility: VisibilityType = Field(
        ...,
        description="Current visibility type of the dashboard (PUBLIC, PRIVATE, or SHARED)",
    )
    shared_with: List[ShareUser] = Field(
        default=[], description="List of users this dashboard is shared with"
    )


class DashboardFilterConfigResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str
