from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, Field
import pandas as pd
from pydantic import field_validator


class WorkflowFundSchema(BaseModel):
    number: str = Field(alias="Segment Value ")
    description: str = Field(alias="Segment Value Description")
    appropriation_fund_value: Optional[str] = Field(alias="Parent Value1")
    appropriation_fund_description: Optional[str] = Field(
        alias="Parent Value1 Description"
    )
    gaap_fund_value: Optional[str] = Field(alias="Parent Value 2")
    gaap_fund_description: Optional[str] = Field(alias="Parent Value Description2")
    gaap_fund_type_value: Optional[str] = Field(alias="Parent Value 3")
    gaap_fund_type_description: Optional[str] = Field(alias="Parent Value Description3")
    gaap_fund_category_value: Optional[str] = Field(alias="Parent Value 4")
    gaap_fund_category_description: Optional[str] = Field(
        alias="Parent Value Description4"
    )


class WorkflowProgramSchema(BaseModel):
    number: str = Field(alias="Segment Value ")
    description: str = Field(alias="Segment Value Description")
    activity_number: Optional[str] = Field(alias="Parent Value1")
    activity_description: Optional[str] = Field(alias="Parent Value1 Description")
    program_number: Optional[str] = Field(alias="Parent Value 2")
    program_description: Optional[str] = Field(alias="Parent Value Description2")


class WorkflowCostCenterSchema(BaseModel):
    number: str = Field(alias="Segment Value ")
    description: str = Field(alias="Segment Value Description")
    division_value: Optional[str] = Field(alias="Parent Value1")
    division_description: Optional[str] = Field(alias="Parent Value1 Description")
    department_value: Optional[str] = Field(alias="Parent Value 2")
    department_description: Optional[str] = Field(alias="Parent Value Description2")


class WorkflowAccountSchema(BaseModel):
    number: str = Field(alias="Segment Value ")
    description: str = Field(alias="Segment Value Description")
    account_group_value: Optional[str] = Field(alias="Parent Value1")
    account_group_description: Optional[str] = Field(alias="Parent Value1 Description")
    account_class_value: Optional[str] = Field(alias="Parent Value 2")
    account_class_description: Optional[str] = Field(alias="Parent Value Description2")
    account_category_value: Optional[str] = Field(alias="Parent Value 3")
    account_category_description: Optional[str] = Field(
        alias="Parent Value Description3"
    )
    account_type_value: Optional[str] = Field(alias="Parent Value 4")
    account_type_description: Optional[str] = Field(alias="Parent Value Description4")


class WorkflowAwardSchema(BaseModel):
    number: str
    name: str
    organization: str
    start_date: date
    end_date: date
    closed_date: Optional[date]
    status: str
    award_type: str


class WorkflowProjectSchema(BaseModel):
    owning_agency: Optional[str] = Field(default=None)
    principal_investigator: Optional[str]
    number: str
    name: str
    description: Optional[str]
    project_type: str
    organization: Optional[str]
    master_project_number: Optional[str]
    primary_category: Optional[str]
    project_category: Optional[str]
    project_classification: Optional[str]
    ward: Optional[str]
    fhwa_improvement_types: Optional[str]
    fhwa_functional_codes: Optional[str]
    fhwa_capital_outlay_category: Optional[str]
    fhwa_system_code: Optional[str]
    nhs: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status_code: Optional[str]
    owner_agency: Optional[str]
    award_project_burden_schedule_name: Optional[str]
    iba_project_number: Optional[str]
    burden_rate_multiplier: Optional[float]
    burden_schedule_version_start_date: Optional[date]
    burden_schedule_version_end_date: Optional[date]
    burden_schedule_version_name: Optional[str]
    ind_rate_sch_id: Optional[str]
    chargeable_flag: Optional[bool]
    billable_flag: Optional[bool]
    capitalizable_flag: Optional[bool]
    cost_center_id: Optional[int]
    program_id: Optional[int]
    sponsor_id: Optional[int]


class WorkflowSponsorSchema(BaseModel):
    name: str
    number: str
    award_number: Optional[str]


class WorkflowParentTaskSchema(BaseModel):
    name: str
    number: str
    project_id: int


class WorkflowSubTaskSchema(BaseModel):
    name: Optional[str] = None
    number: str
    parent_task_id: int
    start_date: Optional[date]
    completion_date: Optional[date]
    award_funding_amount: Optional[float] = Field(default=None)
    png_lifetime_budget: Optional[float] = Field(default=None)
    png_lifetime_allotment: Optional[float] = Field(default=None)
    commitment: Optional[float] = Field(default=None)
    obligation: Optional[float] = Field(default=None)
    expenditure: Optional[float] = Field(default=None)
    receivables: Optional[float] = Field(default=None)
    revenue: Optional[float] = Field(default=None)
    fund_id: Optional[int] = Field(default=None)
    award_id: int


class WorkflowTransactionSchema(BaseModel):
    sub_task_id: int
    award_id: int
    transaction_number: Optional[str] = None
    transaction_source: Optional[str] = None
    expenditure_type: Optional[str] = None
    expenditure_category: Optional[str] = None
    expenditure_organization: Optional[str] = None
    expenditure_item_date: Optional[date] = None
    accounting_period: Optional[str] = None
    unit_of_measure: Optional[str] = None
    incurred_by_person: Optional[str] = None
    person_number: Optional[str] = None
    position_number: Optional[str] = None
    vendor_name: Optional[str] = None
    po_number: Optional[str] = None
    po_line_number: Optional[str] = None
    ap_invoice_number: Optional[str] = None
    ap_invoice_line_number: Optional[str] = None
    dist_line_num: Optional[str] = None
    invoice_date: Optional[date] = None
    check_number: Optional[str] = None
    check_date: Optional[date] = None
    expenditure_batch: Optional[str] = None
    expenditure_comment: Optional[str] = None
    orig_transaction_reference: Optional[str] = None
    capitalizable_flag: Optional[bool] = None
    billable_flag: Optional[bool] = None
    bill_hold_flag: Optional[bool] = None
    revenue_status: Optional[str] = None
    transaction_ar_invoice_status: Optional[str] = None
    servicedate_from: Optional[date] = None
    servicedate_to: Optional[date] = None
    gl_batch_name: Optional[str] = None
    quantity: Optional[float] = None
    transaction_amount: Optional[float] = None
    burdened_amount: Optional[float] = None
    rate: Optional[float] = None

class WorkflowProjectSchemaForValidation(WorkflowProjectSchema):
    cost_center_id: Optional[Union[int,str]]
    program_id: Optional[Union[int,str]]
    sponsor_id: Optional[Union[int,str]]

    @field_validator("burden_schedule_version_end_date", mode="before")
    def convert_nat_to_none(cls, v):
        if isinstance(v, pd._libs.tslibs.nattype.NaTType):
            return None
        return v

    @field_validator("cost_center_id", "program_id", "sponsor_id", mode="before")
    def convert_str_to_int(cls, v):
        if v in (None, "", "NaN"):
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return v

class WorkflowTransactionSchemaForValidation(WorkflowTransactionSchema):
    sub_task_id: Optional[str] = None
    award_id: Optional[str] = None