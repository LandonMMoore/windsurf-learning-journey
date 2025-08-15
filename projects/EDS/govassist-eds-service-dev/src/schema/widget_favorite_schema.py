from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import FindBase, FindResult, SearchOptions, make_optional
from src.schema.dashboard_widget_schema import DashboardWidgetInfo


class WidgetFavoriteBase(BaseModel):
    user_id: int
    widget_id: int


class WidgetFavoriteCreate(WidgetFavoriteBase):
    pass


class WidgetFavoriteInfo(WidgetFavoriteBase):
    id: int
    widget: DashboardWidgetInfo

    class Config:
        from_attributes = True


class WidgetFavoriteToggleResponse(BaseModel):
    widget_id: int
    is_favorite: bool


class WidgetFavoriteFind(make_optional(FindBase), make_optional(WidgetFavoriteBase)):
    pass


class WidgetFavoriteListResponse(FindResult):
    founds: Optional[List[WidgetFavoriteInfo]] = None
    search_options: Optional[SearchOptions] = None
