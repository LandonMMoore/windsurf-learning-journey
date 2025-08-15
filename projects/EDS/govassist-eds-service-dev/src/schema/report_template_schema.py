from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from src.schema.base_schema import FindBase, ModelBaseInfo, make_optional
from src.util.regex_validator import validate_alphanumerical_with_spaces


class ReportTemplateTagSchema(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class ReportTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None


class ReportTemplateConfigBase(ReportTemplateBase):

    config: list[dict]


class ReportTemplateCreateBase(ReportTemplateConfigBase):
    tags: Optional[list[int]] = None

    @field_validator("name", mode="before")
    def validate_fields(cls, v, info):
        if v is None:
            return v
        if not str(v).strip():
            raise ValueError("Field cannot be empty or whitespace")
        return str(v).strip()

    _validate_name = validate_alphanumerical_with_spaces(
        "name",
        " must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )


class ReportTemplateExtractBase(ReportTemplateBase):
    report_id: int
    created_by_id: Optional[int] = None

    @field_validator("name", mode="before")
    def validate_fields(cls, v, info):
        if v is None:
            return v
        if not str(v).strip():
            raise ValueError("Field cannot be empty or whitespace")
        return str(v).strip()

    _validate_name = validate_alphanumerical_with_spaces(
        "name",
        " must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )


class ReportTemplateCreate(ReportTemplateCreateBase):
    created_by_id: Optional[int] = None

class ReportTemplateCreateExcludeTags(ReportTemplateConfigBase):
    created_by_id: Optional[int] = None

class ReportTemplateUpdate(make_optional(ReportTemplateCreateBase)):
    pass


class ReportTemplateInfo(ModelBaseInfo, ReportTemplateConfigBase):
    tags: Optional[list[ReportTemplateTagSchema]] = None
    model_config = ConfigDict(from_attributes=True)
    is_predefined: bool


class ReportTemplateFind(make_optional(FindBase), make_optional(ReportTemplateBase)):
    pass


class ReportTemplateListResponse(BaseModel):
    founds: list[ReportTemplateInfo]
    search_options: dict
