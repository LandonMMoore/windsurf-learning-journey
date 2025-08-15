from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from src.schema.award_schema import AwardInfo
from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)
from src.schema.cost_center_schema import CostCenterInfo
from src.schema.fhwa_schema import (
    FhwaCategoriesInfo,
    FhwaInfo,
    FhwaProgramCodeInfo,
    FhwaProjectNumberInfo,
    FhwaSoarGrantInfo,
    FhwaSoarProjectNoInfo,
    FhwaStipReferenceInfo,
)
from src.schema.master_project_schema import MasterProjectInfo
from src.schema.organization_schema import OrganizationInfo
from src.schema.par_award_association_schema import ParAwardAssociationInfo
from src.schema.project_location_schema import ProjectLocationInfo
from src.util.regex_validator import (
    validate_funding_source,
    validate_name_with_alphanumerical,
)


class ProjectDetailBase(BaseModel):
    project_name: Optional[str] = None
    project_number: Optional[str] = None
    award_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    program_code: Optional[str] = None
    account_group: Optional[str] = None
    project_status: Optional[str] = None
    account_detail: Optional[str] = None
    project_type: Optional[str] = None
    icrs_exempt: Optional[bool] = None
    icrs_rate: Optional[float] = None
    fhwa_program_code_id: Optional[int] = None
    fund_number: Optional[int] = None
    # program_parent_id: Optional[int] = None
    # parent_account_id: Optional[int] = None
    funding_source: Optional[str] = None
    current_project_end_date: Optional[date] = None
    request_end_date: Optional[date] = None
    project_location_id: Optional[int] = None
    budget_analyst: Optional[str] = None
    reason_for_extension: Optional[str] = None
    asset_type: Optional[str] = None
    improvement_type: Optional[str] = None
    project_manager: Optional[str] = None
    recipient_project_number: Optional[str] = None
    award_type: Optional[str] = None
    contract_number: Optional[str] = None
    bridge_number: Optional[str] = None
    gis_route_id: Optional[str] = None
    beginning_point: Optional[str] = None
    end_point: Optional[str] = None
    fap_number: Optional[str] = None


class ProjectDetailCreateBase(BaseModel):
    project_name: Optional[str] = Field(default=None, min_length=2)
    project_number: Optional[str] = Field(default=None, min_length=2)
    award_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    program_code: Optional[str] = Field(default=None, min_length=2)
    account_group: Optional[str] = Field(default=None, min_length=2)
    project_status: Optional[str] = Field(default=None, min_length=2)
    account_detail: Optional[str] = Field(default=None, min_length=2)
    project_type: Optional[str] = Field(default=None, min_length=2)
    icrs_exempt: Optional[bool] = None
    icrs_rate: Optional[float] = None
    fhwa_program_code_id: Optional[int] = None
    fhwa_project_number_id: Optional[int] = None
    fhwa_soar_grant_id: Optional[int] = None
    fhwa_soar_project_no_id: Optional[int] = None
    fhwa_stip_reference_id: Optional[int] = None
    fhwa_categories_id: Optional[int] = None
    master_project_id: Optional[int] = None
    eds_organization_id: Optional[int] = None
    fund_number: Optional[int] = None
    # program_parent_id: Optional[int] = None
    # parent_account_id: Optional[int] = None
    funding_source: Optional[str] = Field(default=None, min_length=2)
    current_project_end_date: Optional[date] = None
    request_end_date: Optional[date] = None
    project_location_id: Optional[int] = None
    budget_analyst: Optional[str] = Field(default=None, min_length=2)
    reason_for_extension: Optional[str] = Field(default=None, min_length=2)
    asset_type: Optional[str] = Field(default=None, min_length=2)
    improvement_type: Optional[str] = Field(default=None, min_length=2)
    project_manager: Optional[str] = Field(default=None, min_length=2)
    recipient_project_number: Optional[str] = Field(default=None, min_length=2)
    award_type: Optional[str] = Field(default=None, min_length=2)
    contract_number: Optional[str] = Field(default=None, min_length=2)
    bridge_number: Optional[str] = Field(default=None, min_length=2)
    gis_route_id: Optional[str] = Field(default=None, min_length=2)
    beginning_point: Optional[str] = Field(default=None, min_length=2)
    end_point: Optional[str] = Field(default=None, min_length=2)
    fap_number: Optional[str] = None

    @validator(
        "project_name",
        "project_number",
        "program_code",
        "account_group",
        "project_status",
        "account_detail",
        "project_type",
        "funding_source",
        "budget_analyst",
        "reason_for_extension",
        "asset_type",
        "improvement_type",
        "project_manager",
        "recipient_project_number",
        "award_type",
        "contract_number",
        "bridge_number",
        "gis_route_id",
        "beginning_point",
        "end_point",
        "fap_number",
        "funding_source",
        pre=True,
        always=True,
    )
    def validate_fields(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class ProjectDetailCreateRequest(ProjectDetailCreateBase):
    award_type_ids: Optional[List[int]] = None
    par_id: Optional[int] = None

    _validate_project_number = validate_name_with_alphanumerical(
        "project_number",
        "Project number must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )
    _validate_program_code = validate_name_with_alphanumerical(
        "program_code",
        "Program code must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )
    _validate_project_status = validate_name_with_alphanumerical(
        "project_status",
        "Project status must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )
    _validate_funding_source = validate_funding_source(
        "funding_source",
        "Funding source must be one of the following: federal_grant, local",
    )


class ProjectDetailCreate(ProjectDetailCreateBase):
    pass


class ProjectDetailUpdate(ProjectDetailCreateBase):
    _validate_project_number = validate_name_with_alphanumerical(
        "project_number",
        "Project number must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )
    _validate_program_code = validate_name_with_alphanumerical(
        "program_code",
        "Program code must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )
    _validate_project_status = validate_name_with_alphanumerical(
        "project_status",
        "Project status must contain only letters, numbers, dashes, and underscores with single spaces between words",
    )
    _validate_funding_source = validate_funding_source(
        "funding_source",
        "Funding source must be one of the following: federal_grant, local",
    )


class ProjectDetailFind(make_optional(FindBase), make_optional(ProjectDetailBase)):
    pass


class ProjectDetailInfo(ModelBaseInfo, ProjectDetailBase):
    award: Optional[AwardInfo] = None
    cost_center: Optional[CostCenterInfo] = None
    fhwa: Optional[FhwaInfo] = None
    master_project: Optional[MasterProjectInfo] = None
    organization: Optional[OrganizationInfo] = None
    project_location: Optional[ProjectLocationInfo] = None
    fhwa_program_code: Optional[FhwaProgramCodeInfo] = None
    fhwa_project_number: Optional[FhwaProjectNumberInfo] = None
    fhwa_soar_grant: Optional[FhwaSoarGrantInfo] = None
    fhwa_soar_project_no: Optional[FhwaSoarProjectNoInfo] = None
    fhwa_stip_reference: Optional[FhwaStipReferenceInfo] = None
    fhwa_categories: Optional[FhwaCategoriesInfo] = None
    # award_types: Optional[List[FhwaAwardTypeInfo]] = None
    par_award_associations: Optional[List[ParAwardAssociationInfo]] = None


class ProjectDetailCreateResponse(ModelBaseInfo, ProjectDetailBase):
    award: Optional[AwardInfo] = None
    cost_center: Optional[CostCenterInfo] = None


class ProjectDetailListResponse(FindResult):
    founds: Optional[List[ProjectDetailInfo]] = None
    search_options: Optional[SearchOptions] = None


class ProjectDetailWithPar(BaseModel):
    project_manager: Optional[str] = None
    funding_source: Optional[str] = None
    fap_number: Optional[str] = None
    project_number: Optional[str] = None
    budget_analyst: Optional[str] = None
