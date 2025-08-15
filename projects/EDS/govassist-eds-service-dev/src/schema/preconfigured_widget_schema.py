from typing import Optional

from pydantic import BaseModel, constr, field_validator

from src.schema.base_schema import FindBase, ModelBaseInfo, make_optional


class PreconfiguredWidgetBase(BaseModel):
    name: str
    description: str
    widget_type: str
    image_url: str
    data_source: str
    category: str
    category_label: Optional[str] = None
    filters: Optional[dict] = {}


class PreconfiguredWidgetCreateBase(BaseModel):
    name: constr(min_length=2)
    description: constr(min_length=2)
    widget_type: constr(min_length=2)
    image_url: Optional[str] = None
    data_source: constr(min_length=2)
    config: Optional[dict] = {}
    category: constr(min_length=2)
    category_label: constr(min_length=2)


class PreconfiguredWidgetCreate(PreconfiguredWidgetCreateBase):
    pass


class PreconfiguredWidgetUpdate(make_optional(PreconfiguredWidgetCreateBase)):
    pass


class PreconfiguredWidgetInfo(ModelBaseInfo, PreconfiguredWidgetBase):
    config: Optional[dict] = {}


class PreconfiguredWidgetFind(
    make_optional(FindBase), make_optional(PreconfiguredWidgetBase)
):
    pass


class PreconfiguredWidgetListResponse(BaseModel):
    founds: list[PreconfiguredWidgetInfo]
    search_options: dict


class PreconfiguredWidgetSave(BaseModel):
    dashboard_widget_id: int
    category: str
    widget_name: str
    widget_description: str

    @field_validator("category")
    def validate_category(cls, v):
        if v in ["eds_system", "custom", "r025"]:
            raise ValueError(
                "Category cannot be one of the reserved values: 'eds_system', 'custom', or 'r025'"
            )
        return v
