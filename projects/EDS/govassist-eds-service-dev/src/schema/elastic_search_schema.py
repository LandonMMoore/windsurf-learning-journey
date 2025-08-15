from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FederalFundES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    fund_code: Optional[str] = None
    fund_available: Optional[float] = None
    fund_obligations: Optional[float] = None
    fund_unobligated_balance: Optional[float] = None
    fund_pending_obligations: Optional[float] = None
    fund_pending_unobligated_balance: Optional[float] = None
    fund_advance_construction: Optional[float] = None

    class Config:
        from_attributes = True


class AdditionalFundES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    ce: Optional[float] = None
    construction: Optional[float] = None
    feasibility_studies: Optional[float] = None
    design: Optional[float] = None
    rights_of_way: Optional[float] = None
    equipment: Optional[float] = None
    federal_fund: Optional[FederalFundES] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParBudgetAnalysisFundES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    fund_type: Optional[str] = None
    ce: Optional[float] = None
    construction: Optional[float] = None
    feasibility_studies: Optional[float] = None
    design: Optional[float] = None
    rights_of_way: Optional[float] = None
    equipment: Optional[float] = None
    is_requested_fund: Optional[bool] = None
    federal_fund: Optional[FederalFundES] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParBudgetAnalysisES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    ce_rate: Optional[float] = None
    part_rate: Optional[float] = None
    fa_rate: Optional[float] = None
    dc_rate: Optional[float] = None
    justification: Optional[str] = None
    additional_funds: Optional[List[AdditionalFundES]] = Field(
        default=[], alias="additional_fund"
    )
    par_budget_analysis_funds: Optional[List[ParBudgetAnalysisFundES]] = Field(
        default=[], alias="par_budget_analysis_fund"
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class AwardTypeES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AwardES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    award_name: Optional[str] = None
    award_number: Optional[str] = None
    award_start: Optional[datetime] = None
    award_end: Optional[datetime] = None
    award_dfda_no: Optional[str] = None
    award_organization: Optional[str] = None
    award_status: Optional[str] = None
    sponsor: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CostCenterES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    cost_center: Optional[str] = None
    cost_center_name: Optional[str] = None
    cost_center_parent1: Optional[str] = None
    cost_center_parent1_desc: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FhwaES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    program_code: Optional[str] = None
    project_number: Optional[str] = None
    soar_grant: Optional[str] = None
    soar_project_no: Optional[str] = None
    stip_reference: Optional[str] = None
    categories: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterProjectES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    master_project_name: Optional[str] = None
    master_project_number: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    project_organization: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectLocationES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    location: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectDetailsES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    project_name: Optional[str] = None
    project_number: Optional[str] = None
    program_code: Optional[str] = None
    account_group: Optional[str] = None
    project_status: Optional[str] = None
    account_detail: Optional[str] = None
    project_type: Optional[str] = None
    icrs_exempt: Optional[bool] = None
    icrs_rate: Optional[float] = None
    fund_number: Optional[int] = None
    funding_source: Optional[str] = None
    current_project_end_date: Optional[datetime] = None
    request_end_date: Optional[datetime] = None
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
    owner_agency: Optional[str] = None
    program_name: Optional[str] = None
    program_parent1: Optional[str] = None
    program_parent1_description: Optional[str] = None
    account: Optional[str] = None
    account_parent1: Optional[str] = None
    award: Optional[AwardES] = None
    cost_center: Optional[CostCenterES] = None
    fhwa_program_code: Optional[FhwaES] = None
    fhwa_project_number: Optional[FhwaES] = None
    fhwa_soar_grant: Optional[FhwaES] = None
    fhwa_soar_project_no: Optional[FhwaES] = None
    fhwa_stip_reference: Optional[FhwaES] = None
    fhwa_categories: Optional[FhwaES] = None
    master_project: Optional[MasterProjectES] = None
    organization: Optional[OrganizationES] = None
    project_location: Optional[ProjectLocationES] = None
    par_budget_analysis: Optional[List[ParBudgetAnalysisES]] = []
    award_types: Optional[List[AwardTypeES]] = []

    class Config:
        from_attributes = True


class BudgetItemES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    account: Optional[str] = None
    parent_task_number: Optional[str] = None
    parent_task_name: Optional[str] = None
    subtask_number: Optional[str] = None
    lifetime_budget: Optional[float] = None
    initial_allotment: Optional[float] = None
    expenditures: Optional[float] = None
    obligations: Optional[float] = None
    commitments: Optional[float] = None
    current_balance: Optional[float] = None
    lifetime_balance: Optional[float] = None
    proposed_budget: Optional[float] = None
    change_amount: Optional[float] = None
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetInfoBaseES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    task_name: Optional[str] = None
    proposed_budget: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetInfoES(BudgetInfoBaseES):
    budget_items: Optional[List[BudgetItemES]] = []


class ParActivityES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    activity: Optional[str] = None
    comments: Optional[str] = None
    date: Optional[datetime] = None
    status: Optional[str] = None
    user: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParES(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    epar_name: Optional[str] = None
    ai_summary: Optional[str] = None
    status: Optional[str] = None
    request_type: Optional[str] = None
    justification: Optional[str] = None
    description: Optional[str] = None
    master_project_name: Optional[str] = None
    award_sponsor: Optional[str] = None
    location: Optional[str] = None
    total_project_budget: Optional[float] = None
    fund_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_details: Optional[ProjectDetailsES] = None
    budget_info: Optional[List[BudgetInfoES]] = []
    par_activities: Optional[List[ParActivityES]] = []

    class Config:
        from_attributes = True
