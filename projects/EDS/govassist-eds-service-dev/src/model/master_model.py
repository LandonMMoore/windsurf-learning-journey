from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String

from src.model.base_model import SoftDeleteMixin


class MasterFund(SoftDeleteMixin):
    __tablename__ = "master_funds"
    __col_name_prefix__ = "Fund"

    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False, info={"display_name": "Fund Number"})
    description = Column(
        String, nullable=False, info={"display_name": "Fund Description"}
    )
    appropriation_fund_value = Column(
        String, nullable=True, info={"display_name": "Appropriation Fund Value"}
    )
    appropriation_fund_description = Column(
        String, nullable=True, info={"display_name": "Appropriation Fund Description"}
    )
    gaap_fund_value = Column(
        String, nullable=True, info={"display_name": "GAAP Fund Value"}
    )
    gaap_fund_description = Column(
        String, nullable=True, info={"display_name": "GAAP Fund Description"}
    )
    gaap_fund_type_value = Column(
        String, nullable=True, info={"display_name": "GAAP Fund Type Value"}
    )
    gaap_fund_type_description = Column(
        String, nullable=True, info={"display_name": "GAAP Fund Type Description"}
    )
    gaap_fund_category_value = Column(
        String, nullable=True, info={"display_name": "GAAP Fund Category Value"}
    )
    gaap_fund_category_description = Column(
        String, nullable=True, info={"display_name": "GAAP Fund Category Description"}
    )


class MasterProgram(SoftDeleteMixin):
    __tablename__ = "master_programs"
    __col_name_prefix__ = "Program"
    id = Column(Integer, primary_key=True)
    number = Column(
        String, nullable=False, info={"display_name": "Program Service Number"}
    )
    description = Column(
        String, nullable=False, info={"display_name": "Program Service Description"}
    )
    activity_number = Column(
        String, nullable=True, info={"display_name": "Activity Number"}
    )
    activity_description = Column(
        String, nullable=True, info={"display_name": "Activity Description"}
    )
    program_number = Column(
        String, nullable=True, info={"display_name": "Program Number"}
    )
    program_description = Column(
        String, nullable=True, info={"display_name": "Program Description"}
    )


class MasterCostCenter(SoftDeleteMixin):
    __tablename__ = "master_cost_centers"
    __col_name_prefix__ = "Cost Center"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False, info={"display_name": "Cost Center Number"})
    description = Column(
        String, nullable=False, info={"display_name": "Cost Center Description"}
    )
    division_value = Column(
        String, nullable=True, info={"display_name": "Division Value"}
    )
    division_description = Column(
        String, nullable=True, info={"display_name": "Division Description"}
    )
    department_value = Column(
        String, nullable=True, info={"display_name": "Department Value"}
    )
    department_description = Column(
        String, nullable=True, info={"display_name": "Department Description"}
    )


class MasterAccount(SoftDeleteMixin):
    __tablename__ = "master_accounts"
    __col_name_prefix__ = "Account"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False, info={"display_name": "Account Number"})
    description = Column(
        String, nullable=False, info={"display_name": "Account Description"}
    )
    account_group_value = Column(
        String, nullable=True, info={"display_name": "Account Group Value"}
    )
    account_group_description = Column(
        String, nullable=True, info={"display_name": "Account Group Description"}
    )
    account_class_value = Column(
        String, nullable=True, info={"display_name": "Account Class Value"}
    )
    account_class_description = Column(
        String, nullable=True, info={"display_name": "Account Class Description"}
    )
    account_category_value = Column(
        String, nullable=True, info={"display_name": "Account Category Value"}
    )
    account_category_description = Column(
        String, nullable=True, info={"display_name": "Account Category Description"}
    )
    account_type_value = Column(
        String, nullable=True, info={"display_name": "Account Type Value"}
    )
    account_type_description = Column(
        String, nullable=True, info={"display_name": "Account Type Description"}
    )


class MasterProjectDetails(SoftDeleteMixin):
    __tablename__ = "master_project_details"
    __col_name_prefix__ = "Project"

    id = Column(Integer, primary_key=True)
    owning_agency = Column(
        String, nullable=False, info={"display_name": "Owning Agency"}
    )
    principal_investigator = Column(
        String, nullable=True, info={"display_name": "Principal Investigator"}
    )
    number = Column(String, nullable=False, info={"display_name": "Project Number"})
    name = Column(String, nullable=False, info={"display_name": "Project Name"})
    description = Column(
        String, nullable=True, info={"display_name": "Project Description"}
    )
    project_type = Column(String, nullable=False, info={"display_name": "Project Type"})
    organization = Column(
        String, nullable=True, info={"display_name": "Project Organization"}
    )
    master_project_number = Column(
        String, nullable=True, info={"display_name": "Master Project Number"}
    )
    primary_category = Column(
        String, nullable=True, info={"display_name": "Primary Category"}
    )
    project_category = Column(
        String, nullable=True, info={"display_name": "Project Category"}
    )
    project_classification = Column(
        String, nullable=True, info={"display_name": "Project Classification"}
    )
    ward = Column(String, nullable=True, info={"display_name": "Ward"})
    fhwa_improvement_types = Column(
        String, nullable=True, info={"display_name": "FHWA Improvement Types"}
    )
    fhwa_functional_codes = Column(
        String, nullable=True, info={"display_name": "FHWA Functional Codes"}
    )
    fhwa_capital_outlay_category = Column(
        String, nullable=True, info={"display_name": "FHWA Capital Outlay Category"}
    )
    fhwa_system_code = Column(
        String, nullable=True, info={"display_name": "FHWA System Code"}
    )
    nhs = Column(String, nullable=True, info={"display_name": "NHS"})
    start_date = Column(
        Date, nullable=True, info={"display_name": "Project Start Date"}
    )
    end_date = Column(Date, nullable=True, info={"display_name": "Project End Date"})
    status_code = Column(
        String, nullable=True, info={"display_name": "Project Status Code"}
    )
    owner_agency = Column(
        String, nullable=True, info={"display_name": "Project Owner Agency"}
    )
    award_project_burden_schedule_name = Column(
        String,
        nullable=True,
        info={"display_name": "Award Project Burden Schedule Name"},
    )
    iba_project_number = Column(
        String, nullable=True, info={"display_name": "IBA Project Number"}
    )
    burden_rate_multiplier = Column(
        Float, nullable=True, info={"display_name": "Burden Rate Multiplier"}
    )
    burden_schedule_version_start_date = Column(
        Date, nullable=True, info={"display_name": "Burden Schedule Version Start Date"}
    )
    burden_schedule_version_end_date = Column(
        Date, nullable=True, info={"display_name": "Burden Schedule Version End Date"}
    )
    burden_schedule_version_name = Column(
        String, nullable=True, info={"display_name": "Burden Schedule Version Name"}
    )
    ind_rate_sch_id = Column(
        String, nullable=True, info={"display_name": "Ind Rate Sch ID"}
    )
    chargeable_flag = Column(
        Boolean, nullable=True, info={"display_name": "Chargeable Flag"}
    )
    billable_flag = Column(
        Boolean, nullable=True, info={"display_name": "Billable Flag"}
    )
    capitalizable_flag = Column(
        Boolean, nullable=True, info={"display_name": "Capitalizable Flag"}
    )
    cost_center_id = Column(
        Integer, ForeignKey("master_cost_centers.id"), nullable=True
    )
    program_id = Column(Integer, ForeignKey("master_programs.id"), nullable=True)
    sponsor_id = Column(Integer, ForeignKey("master_sponsors.id"), nullable=True)


class MasterAward(SoftDeleteMixin):
    __tablename__ = "master_awards"
    __col_name_prefix__ = "Award"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False, info={"display_name": "Award Number"})
    name = Column(String, nullable=False, info={"display_name": "Award Name"})
    organization = Column(
        String, nullable=False, info={"display_name": "Award Organization"}
    )
    start_date = Column(Date, nullable=False, info={"display_name": "Award Start Date"})
    end_date = Column(Date, nullable=False, info={"display_name": "Award End Date"})
    closed_date = Column(
        Date, nullable=True, info={"display_name": "Award Closed Date"}
    )
    status = Column(String, nullable=False, info={"display_name": "Award Status"})
    award_type = Column(String, nullable=False, info={"display_name": "Award Type"})


class MasterSponsor(SoftDeleteMixin):
    __tablename__ = "master_sponsors"
    __col_name_prefix__ = "Sponsor"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, info={"display_name": "Sponsor Name"})
    number = Column(String, nullable=False, info={"display_name": "Sponsor Number"})
    award_number = Column(
        String, nullable=True, info={"display_name": "Sponsor Award Number"}
    )


class MasterParentTask(SoftDeleteMixin):
    __tablename__ = "master_parent_tasks"
    __col_name_prefix__ = "Parent Task"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, info={"display_name": "Parent Task Name"})
    number = Column(String, nullable=False, info={"display_name": "Parent Task Number"})
    project_id = Column(
        Integer, ForeignKey("master_project_details.id"), nullable=False
    )


class MasterSubTask(SoftDeleteMixin):
    __tablename__ = "master_sub_tasks"
    __col_name_prefix__ = "Sub Task"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, info={"display_name": "Sub Task Name"})
    number = Column(String, nullable=False, info={"display_name": "Sub Task Number"})
    parent_task_id = Column(
        Integer, ForeignKey("master_parent_tasks.id"), nullable=False
    )
    fund_id = Column(Integer, ForeignKey("master_funds.id"))
    award_id = Column(Integer, ForeignKey("master_awards.id"), nullable=False)
    start_date = Column(
        Date, nullable=True, info={"display_name": "Sub Task Start Date"}
    )
    completion_date = Column(
        Date, nullable=True, info={"display_name": "Sub Task Completion Date"}
    )
    award_funding_amount = Column(
        Float, nullable=True, info={"display_name": "Award Funding Amount"}
    )
    png_lifetime_budget = Column(
        Float, nullable=True, info={"display_name": "PNG Lifetime Budget"}
    )
    png_lifetime_allotment = Column(
        Float, nullable=True, info={"display_name": "PNG Lifetime Allotment"}
    )
    commitment = Column(Float, nullable=True, info={"display_name": "Commitment"})
    obligation = Column(Float, nullable=True, info={"display_name": "Obligation"})
    expenditure = Column(Float, nullable=True, info={"display_name": "Expenditure"})
    receivables = Column(Float, nullable=True, info={"display_name": "Receivables"})
    revenue = Column(Float, nullable=True, info={"display_name": "Revenue"})


class MasterTransaction(SoftDeleteMixin):
    __tablename__ = "master_transactions"
    __col_name_prefix__ = "Transaction"
    id = Column(Integer, primary_key=True)
    sub_task_id = Column(Integer, ForeignKey("master_sub_tasks.id"), nullable=False)
    award_id = Column(Integer, ForeignKey("master_awards.id"), nullable=False)
    transaction_number = Column(
        String, nullable=False, info={"display_name": "Transaction Number"}
    )
    transaction_source = Column(
        String, nullable=False, info={"display_name": "Transaction Source"}
    )
    expenditure_type = Column(
        String, nullable=False, info={"display_name": "Expenditure Type"}
    )
    expenditure_category = Column(
        String, nullable=False, info={"display_name": "Expenditure Category"}
    )
    expenditure_organization = Column(
        String, nullable=False, info={"display_name": "Expenditure Organization"}
    )
    expenditure_item_date = Column(
        Date, nullable=False, info={"display_name": "Expenditure Item Date"}
    )
    accounting_period = Column(
        String, nullable=False, info={"display_name": "Accounting Period"}
    )
    unit_of_measure = Column(
        String, nullable=True, info={"display_name": "Unit of Measure"}
    )
    incurred_by_person = Column(
        String, nullable=True, info={"display_name": "Incurred By Person"}
    )
    person_number = Column(
        String, nullable=True, info={"display_name": "Person Number"}
    )
    position_number = Column(
        String, nullable=True, info={"display_name": "Position Number"}
    )
    vendor_name = Column(String, nullable=True, info={"display_name": "Vendor Name"})
    po_number = Column(String, nullable=True, info={"display_name": "PO Number"})
    po_line_number = Column(
        String, nullable=True, info={"display_name": "PO Line Number"}
    )
    ap_invoice_number = Column(
        String, nullable=True, info={"display_name": "AP Invoice Number"}
    )
    ap_invoice_line_number = Column(
        String, nullable=True, info={"display_name": "AP Invoice Line Number"}
    )
    dist_line_num = Column(
        String, nullable=True, info={"display_name": "Dist Line Num"}
    )
    invoice_date = Column(Date, nullable=True, info={"display_name": "Invoice Date"})
    check_number = Column(String, nullable=True, info={"display_name": "Check Number"})
    check_date = Column(Date, nullable=True, info={"display_name": "Check Date"})
    expenditure_batch = Column(
        String, nullable=True, info={"display_name": "Expenditure Batch"}
    )
    expenditure_comment = Column(
        String, nullable=True, info={"display_name": "Expenditure Comment"}
    )
    orig_transaction_reference = Column(
        String, nullable=True, info={"display_name": "Orig Transaction Reference"}
    )
    capitalizable_flag = Column(
        Boolean, nullable=True, info={"display_name": "Capitalizable Flag"}
    )
    billable_flag = Column(
        Boolean, nullable=True, info={"display_name": "Billable Flag"}
    )
    bill_hold_flag = Column(
        Boolean, nullable=True, info={"display_name": "Bill Hold Flag"}
    )
    revenue_status = Column(
        String, nullable=True, info={"display_name": "Revenue Status"}
    )
    transaction_ar_invoice_status = Column(
        String, nullable=True, info={"display_name": "Transaction AR Invoice Status"}
    )
    servicedate_from = Column(
        Date, nullable=True, info={"display_name": "Service Date From"}
    )
    servicedate_to = Column(
        Date, nullable=True, info={"display_name": "Service Date To"}
    )
    gl_batch_name = Column(
        String, nullable=True, info={"display_name": "GL Batch Name"}
    )
    quantity = Column(Float, nullable=True, info={"display_name": "Quantity"})
    transaction_amount = Column(
        Float, nullable=True, info={"display_name": "Transaction Amount"}
    )
    burdened_amount = Column(
        Float, nullable=True, info={"display_name": "Burdened Amount"}
    )
    rate = Column(Float, nullable=True, info={"display_name": "Rate"})
