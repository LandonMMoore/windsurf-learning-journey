from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import FindBase, FindResult, SearchOptions, make_optional
from src.schema.dashboard_schema import DashboardInfo


class DashboardFavoriteBase(BaseModel):
    user_id: int
    dashboard_id: int


class DashboardFavoriteCreate(DashboardFavoriteBase):
    pass


class DashboardFavoriteInfo(DashboardFavoriteBase):
    id: int
    dashboard: DashboardInfo

    class Config:
        from_attributes = True


class DashboardFavoriteToggleResponse(BaseModel):
    dashboard_id: int
    is_favorite: bool


class DashboardFavoriteFind(
    make_optional(FindBase), make_optional(DashboardFavoriteBase)
):
    pass


class DashboardFavoriteListResponse(FindResult):
    founds: Optional[List[DashboardFavoriteInfo]] = None
    search_options: Optional[SearchOptions] = None
