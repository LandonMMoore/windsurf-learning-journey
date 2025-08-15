from typing import Optional

from pydantic import BaseModel, constr, validator

from src.schema.base_schema import FindBase, ModelBaseInfo, make_optional
from src.schema.project_detail_schema import ProjectDetailWithPar

# Define regex pattern for allowed characters
# Allows: letters, numbers, spaces, basic punctuation (.,-()&)
ALPHANUMERIC_PATTERN = r"^[a-zA-Z0-9\s.,\-()&_/]+$"


class ParBase(BaseModel):
    project_details_id: Optional[int] = None
    epar_name: str
    status: Optional[str] = None
    request_type: Optional[str] = None
    justification: Optional[str] = None
    description: Optional[str] = None
    master_project_name: Optional[str] = None
    award_sponsor: Optional[str] = None
    location: Optional[str] = None
    current_status: Optional[str] = None
    total_project_budget: Optional[float] = None
    fund_name: Optional[str] = None


class ParCreateBase(BaseModel):
    project_details_id: Optional[int] = None
    epar_name: constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)
    status: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    request_type: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    justification: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    description: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    master_project_name: Optional[
        constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)
    ] = None
    award_sponsor: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    location: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    fund_name: Optional[constr(min_length=2, pattern=ALPHANUMERIC_PATTERN)] = None
    total_project_budget: Optional[float] = None

    @validator(
        "epar_name",
        "status",
        "request_type",
        "justification",
        "description",
        "master_project_name",
        "award_sponsor",
        "location",
        "fund_name",
        pre=True,
        always=True,
    )
    def validate_fields(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class ParCreate(ParCreateBase):
    pass


class ParUpdate(make_optional(ParCreateBase)):
    pass


class ParInfo(ModelBaseInfo, ParBase):
    pass


class ParFind(make_optional(FindBase), make_optional(ParBase)):
    pass


class ParProjectDetail(ModelBaseInfo, make_optional(ParBase)):
    project_details: Optional[ProjectDetailWithPar]


class ParListResponse(BaseModel):
    founds: list[ParProjectDetail]
    search_options: dict


class ParData(BaseModel):
    project_details_project_number: str
    soar_project_number: str
    fap_number: Optional[str] = None
    stip_number: Optional[str] = None
    program: int
    cost_center_name: str
