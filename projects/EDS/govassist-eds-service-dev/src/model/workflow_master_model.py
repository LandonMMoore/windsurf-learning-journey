from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Text

from src.model.base_model import SoftDeleteMixin


class WorkflowMasterFund(SoftDeleteMixin):
    __tablename__ = "workflow_master_funds"
    __col_name_prefix__ = "Fund"

    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    appropriation_fund_value = Column(String, nullable=True)
    appropriation_fund_description = Column(String, nullable=True)
    gaap_fund_value = Column(String, nullable=True)
    gaap_fund_description = Column(String, nullable=True)
    gaap_fund_type_value = Column(String, nullable=True)
    gaap_fund_type_description = Column(String, nullable=True)
    gaap_fund_category_value = Column(String, nullable=True)
    gaap_fund_category_description = Column(String, nullable=True)


class WorkflowMasterProgram(SoftDeleteMixin):
    __tablename__ = "workflow_master_programs"
    __col_name_prefix__ = "Program"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    activity_number = Column(String, nullable=True)
    activity_description = Column(String, nullable=True)
    program_number = Column(String, nullable=True)
    program_description = Column(String, nullable=True)


class WorkflowMasterCostCenter(SoftDeleteMixin):
    __tablename__ = "workflow_master_cost_centers"
    __col_name_prefix__ = "Cost Center"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    division_value = Column(String, nullable=True)
    division_description = Column(String, nullable=True)
    department_value = Column(String, nullable=True)
    department_description = Column(String, nullable=True)


class WorkflowMasterAccount(SoftDeleteMixin):
    __tablename__ = "workflow_master_accounts"
    __col_name_prefix__ = "Account"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    account_group_value = Column(String, nullable=True)
    account_group_description = Column(String, nullable=True)
    account_class_value = Column(String, nullable=True)
    account_class_description = Column(String, nullable=True)
    account_category_value = Column(String, nullable=True)
    account_category_description = Column(String, nullable=True)
    account_type_value = Column(String, nullable=True)
    account_type_description = Column(String, nullable=True)


class WorkflowMasterProjectDetails(SoftDeleteMixin):
    __tablename__ = "workflow_master_project_details"
    __col_name_prefix__ = "Project"

    id = Column(Integer, primary_key=True)
    owning_agency = Column(String, nullable=False)
    principal_investigator = Column(String, nullable=True)
    number = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    master_project_number = Column(String, nullable=True)
    primary_category = Column(String, nullable=True)
    project_category = Column(String, nullable=True)
    project_classification = Column(String, nullable=True)
    ward = Column(String, nullable=True)
    fhwa_improvement_types = Column(String, nullable=True)
    fhwa_functional_codes = Column(String, nullable=True)
    fhwa_capital_outlay_category = Column(String, nullable=True)
    fhwa_system_code = Column(String, nullable=True)
    nhs = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status_code = Column(String, nullable=True)
    owner_agency = Column(String, nullable=True)
    award_project_burden_schedule_name = Column(String, nullable=True)
    iba_project_number = Column(String, nullable=True)
    burden_rate_multiplier = Column(Float, nullable=True)
    burden_schedule_version_start_date = Column(Date, nullable=True)
    burden_schedule_version_end_date = Column(Date, nullable=True)
    burden_schedule_version_name = Column(String, nullable=True)
    ind_rate_sch_id = Column(String, nullable=True)
    chargeable_flag = Column(Boolean, nullable=True)
    billable_flag = Column(Boolean, nullable=True)
    capitalizable_flag = Column(Boolean, nullable=True)
    cost_center_id = Column(
        Integer, ForeignKey("workflow_master_cost_centers.id"), nullable=True
    )
    program_id = Column(
        Integer, ForeignKey("workflow_master_programs.id"), nullable=True
    )
    sponsor_id = Column(
        Integer, ForeignKey("workflow_master_sponsors.id"), nullable=True
    )


class WorkflowMasterAward(SoftDeleteMixin):
    __tablename__ = "workflow_master_awards"
    __col_name_prefix__ = "Award"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    name = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    closed_date = Column(Date, nullable=True)
    status = Column(String, nullable=False)
    award_type = Column(String, nullable=False)


class WorkflowMasterSponsor(SoftDeleteMixin):
    __tablename__ = "workflow_master_sponsors"
    __col_name_prefix__ = "Sponsor"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    number = Column(String, nullable=False)
    award_number = Column(String, nullable=True)


class WorkflowMasterParentTask(SoftDeleteMixin):
    __tablename__ = "workflow_master_parent_tasks"
    __col_name_prefix__ = "Parent Task"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    number = Column(String, nullable=False)
    project_id = Column(
        Integer, ForeignKey("workflow_master_project_details.id"), nullable=False
    )


class WorkflowMasterSubTask(SoftDeleteMixin):
    __tablename__ = "workflow_master_sub_tasks"
    __col_name_prefix__ = "Sub Task"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    number = Column(String, nullable=False)
    parent_task_id = Column(
        Integer, ForeignKey("workflow_master_parent_tasks.id"), nullable=False
    )
    fund_id = Column(Integer, ForeignKey("workflow_master_funds.id"))
    award_id = Column(Integer, ForeignKey("workflow_master_awards.id"), nullable=False)
    start_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    award_funding_amount = Column(Float, nullable=True)
    png_lifetime_budget = Column(Float, nullable=True)
    png_lifetime_allotment = Column(Float, nullable=True)
    commitment = Column(Float, nullable=True)
    obligation = Column(Float, nullable=True)
    expenditure = Column(Float, nullable=True)
    receivables = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)


class WorkflowMasterTransaction(SoftDeleteMixin):
    __tablename__ = "workflow_master_transactions"
    __col_name_prefix__ = "Transaction"
    id = Column(Integer, primary_key=True)
    sub_task_id = Column(
        Integer, ForeignKey("workflow_master_sub_tasks.id"), nullable=False
    )
    award_id = Column(Integer, ForeignKey("workflow_master_awards.id"), nullable=False)
    transaction_number = Column(String, nullable=False)
    transaction_source = Column(String, nullable=False)
    expenditure_type = Column(String, nullable=False)
    expenditure_category = Column(String, nullable=True)
    expenditure_organization = Column(String, nullable=False)
    expenditure_item_date = Column(Date, nullable=False)
    accounting_period = Column(String, nullable=False)
    unit_of_measure = Column(String, nullable=True)
    incurred_by_person = Column(String, nullable=True)
    person_number = Column(String, nullable=True)
    position_number = Column(String, nullable=True)
    vendor_name = Column(String, nullable=True)
    po_number = Column(String, nullable=True)
    po_line_number = Column(String, nullable=True)
    ap_invoice_number = Column(String, nullable=True)
    ap_invoice_line_number = Column(String, nullable=True)
    ap_invoice_line_number = Column(String, nullable=True)
    dist_line_num = Column(String, nullable=True)
    invoice_date = Column(Date, nullable=True)
    check_number = Column(String, nullable=True)
    check_date = Column(Date, nullable=True)
    expenditure_batch = Column(String, nullable=True)
    expenditure_comment = Column(String, nullable=True)
    orig_transaction_reference = Column(String, nullable=True)
    capitalizable_flag = Column(Boolean, nullable=True)
    billable_flag = Column(Boolean, nullable=True)
    bill_hold_flag = Column(Boolean, nullable=True)
    revenue_status = Column(String, nullable=True)
    transaction_ar_invoice_status = Column(String, nullable=True)
    servicedate_from = Column(Date, nullable=True)
    servicedate_to = Column(Date, nullable=True)
    gl_batch_name = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    transaction_amount = Column(Float, nullable=True)
    burdened_amount = Column(Float, nullable=True)
    rate = Column(Float, nullable=True)
