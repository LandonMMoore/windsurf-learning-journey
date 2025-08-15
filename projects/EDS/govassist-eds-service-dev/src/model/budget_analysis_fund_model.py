from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class ParBudgetAnalysisFund(BaseModel):
    __tablename__ = "budget_analysis_fund"

    federal_fund_id = Column(Integer, ForeignKey("federal_fund.id"), nullable=False)
    par_budget_id = Column(
        Integer, ForeignKey("par_budget_analysis.id"), nullable=False
    )

    fund_type = Column(String, nullable=True)
    ce = Column(Float, nullable=True)
    construction = Column(Float, nullable=True)
    feasibility_studies = Column(Float, nullable=True)
    design = Column(Float, nullable=True)
    rights_of_way = Column(Float, nullable=True)
    equipment = Column(Float, nullable=True)

    is_requested_fund = Column(Boolean, nullable=False, default=True)

    # relationships
    federal_fund = relationship(
        "FederalFund", back_populates="par_budget_analysis_fund"
    )
    par_budget_analysis = relationship(
        "ParBudgetAnalysis", back_populates="par_budget_analysis_fund"
    )

    eagers = ["federal_fund", "par_budget_analysis"]
