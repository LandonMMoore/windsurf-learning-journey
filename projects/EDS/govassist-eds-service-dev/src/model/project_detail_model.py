from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class ProjectDetails(BaseModel):
    __tablename__ = "project_details"

    project_name = Column(String)
    project_number = Column(String)

    award_id = Column(Integer, ForeignKey("award.id"), nullable=True)
    cost_center_id = Column(Integer, ForeignKey("cost_center.id"), nullable=True)
    program_code = Column(String, nullable=True)
    account_group = Column(String, nullable=True)
    project_status = Column(String, nullable=True)
    account_detail = Column(String, nullable=True)
    project_type = Column(String, nullable=True)
    icrs_exempt = Column(Boolean, nullable=True)
    icrs_rate = Column(Float, nullable=True)

    fhwa_program_code_id = Column(Integer, ForeignKey("fhwa.id"), nullable=True)
    fhwa_project_number_id = Column(Integer, ForeignKey("fhwa.id"), nullable=True)
    fhwa_soar_grant_id = Column(Integer, ForeignKey("fhwa.id"), nullable=True)
    fhwa_soar_project_no_id = Column(Integer, ForeignKey("fhwa.id"), nullable=True)
    fhwa_stip_reference_id = Column(Integer, ForeignKey("fhwa.id"), nullable=True)
    fhwa_categories_id = Column(Integer, ForeignKey("fhwa.id"), nullable=True)

    master_project_id = Column(Integer, ForeignKey("master_project.id"), nullable=True)
    eds_organization_id = Column(
        Integer, ForeignKey("eds_organization.id"), nullable=True
    )
    fund_number = Column(Integer, nullable=True)
    # program_parent_id = Column(Integer, ForeignKey("program_parent.id"), nullable=True)
    # parent_account_id = Column(Integer, ForeignKey("parent_accounts.id"), nullable=True)

    funding_source = Column(String)
    current_project_end_date = Column(Date)
    request_end_date = Column(Date)
    project_location_id = Column(
        Integer, ForeignKey("project_location.id"), nullable=True
    )
    budget_analyst = Column(String)
    reason_for_extension = Column(String)
    asset_type = Column(String)
    improvement_type = Column(String)
    project_manager = Column(String)
    recipient_project_number = Column(String)
    award_type = Column(String)
    contract_number = Column(String)
    bridge_number = Column(String)
    gis_route_id = Column(String)
    beginning_point = Column(String)
    end_point = Column(String)
    fap_number = Column(String, nullable=True)

    # Relationships (Optional, useful for ORM joins)
    award = relationship("Award", back_populates="project_details")
    cost_center = relationship("CostCenter", back_populates="project_details")

    fhwa_program_code = relationship("Fhwa", foreign_keys=[fhwa_program_code_id])
    fhwa_project_number = relationship("Fhwa", foreign_keys=[fhwa_project_number_id])
    fhwa_soar_grant = relationship("Fhwa", foreign_keys=[fhwa_soar_grant_id])
    fhwa_soar_project_no = relationship("Fhwa", foreign_keys=[fhwa_soar_project_no_id])
    fhwa_stip_reference = relationship("Fhwa", foreign_keys=[fhwa_stip_reference_id])
    fhwa_categories = relationship("Fhwa", foreign_keys=[fhwa_categories_id])

    master_project = relationship("MasterProject", back_populates="project_details")
    organization = relationship("Organization", back_populates="project_details")
    project_location = relationship("ProjectLocation", back_populates="project_details")
    par_award_associations = relationship(
        "ParAwardAssociation", back_populates="project_details"
    )
    par_budget_analysis = relationship(
        "ParBudgetAnalysis", back_populates="project_details"
    )
    par = relationship("Par", back_populates="project_details")

    @hybrid_property
    def award_types(self):
        """
        Returns a list of FhwaAwardType objects from par_award_associations.
        This provides easy access to the award types associated with this project detail.
        """
        return [
            assoc.award_type
            for assoc in self.par_award_associations
            if assoc.award_type
        ]

    eagers = [
        "award",
        "cost_center",
        "fhwa_program_code",
        "fhwa_project_number",
        "fhwa_soar_grant",
        "fhwa_soar_project_no",
        "fhwa_stip_reference",
        "fhwa_categories",
        "master_project",
        "organization",
        "project_location",
        "par_award_associations",
        "par_award_associations.award_type",
        "par_budget_analysis",
    ]
