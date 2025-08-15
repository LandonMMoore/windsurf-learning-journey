from sqlalchemy import Column, Float, ForeignKey, Integer, String, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel
from src.model.par_activity_model import ParActivity


class Par(BaseModel):
    __tablename__ = "par"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    project_details_id = Column(
        Integer, ForeignKey("project_details.id"), nullable=True
    )
    epar_name = Column(String, nullable=False)
    ai_summary = Column(String, nullable=True)
    status = Column(String, nullable=True)
    request_type = Column(String, nullable=True)
    justification = Column(String, nullable=True)
    description = Column(String, nullable=True)
    master_project_name = Column(String, nullable=True)
    award_sponsor = Column(String, nullable=True)
    location = Column(String, nullable=True)
    total_project_budget = Column(Float, nullable=True)
    fund_name = Column(String, nullable=True)

    project_details = relationship("ProjectDetails", back_populates="par")
    budget_info = relationship("BudgetInfo", back_populates="par")
    par_activities = relationship("ParActivity", back_populates="par")
    par_budget_analysis = relationship("ParBudgetAnalysis", back_populates="par")

    @hybrid_property
    def current_status(self):
        # First check if we have a manually set value.
        return getattr(self, "_current_status", None)
        # If no manual value, compute from activities.
        # NOTE: Not using this because it's not efficient as it loads all the activities.
        # if not self.par_activities:
        #     return None
        # return sorted(
        #     self.par_activities, key=lambda x: (x.date or "", x.id), reverse=True
        # )[0].status

    @current_status.setter
    def current_status(self, value):
        self._current_status = value

    @current_status.expression
    def current_status(cls):
        latest_activity = (
            select(ParActivity.status)
            .where(ParActivity.par_id == cls.id)
            .order_by(ParActivity.date.desc(), ParActivity.id.desc())
            .limit(1)
            .scalar_subquery()
        )
        return latest_activity

    eagers = [
        "project_details",
        "par_activities",
        "budget_info",
        "budget_info.budget_items",
        "project_details.master_project",
        "project_details.project_location",
        "project_details.cost_center",
        "project_details.par_award_associations",
        "project_details.par_award_associations.award_type",
        "project_details.fhwa_program_code",
        "project_details.fhwa_project_number",
        "project_details.fhwa_soar_grant",
        "project_details.fhwa_soar_project_no",
        "project_details.fhwa_stip_reference",
        "project_details.fhwa_categories",
        "par_budget_analysis",
    ]
