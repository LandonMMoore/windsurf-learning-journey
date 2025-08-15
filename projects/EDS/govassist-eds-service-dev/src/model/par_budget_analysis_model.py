from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class ParBudgetAnalysis(BaseModel):
    __tablename__ = "par_budget_analysis"

    par_id = Column(Integer, ForeignKey("par.id"), nullable=False)
    project_details_id = Column(
        Integer, ForeignKey("project_details.id"), nullable=False
    )
    ce_rate = Column(Float, nullable=True)
    part_rate = Column(Float, nullable=True)
    fa_rate = Column(Float, nullable=True)
    dc_rate = Column(Float, nullable=True)
    justification = Column(String, nullable=True)

    # Relationships
    par = relationship("Par", back_populates="par_budget_analysis")
    project_details = relationship(
        "ProjectDetails", back_populates="par_budget_analysis"
    )
    additional_fund = relationship(
        "AdditionalFund", back_populates="par_budget_analysis"
    )
    par_budget_analysis_fund = relationship(
        "ParBudgetAnalysisFund", back_populates="par_budget_analysis"
    )

    eagers = [
        "par",
        "project_details",
        "additional_fund",
        "par_budget_analysis_fund",
        "additional_fund.federal_fund",
    ]
