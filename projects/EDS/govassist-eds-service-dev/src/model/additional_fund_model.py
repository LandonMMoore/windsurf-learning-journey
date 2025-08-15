from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class AdditionalFund(BaseModel):
    __tablename__ = "additional_fund"

    federal_fund_id = Column(Integer, ForeignKey("federal_fund.id"), nullable=False)
    par_budget_analysis_id = Column(
        Integer, ForeignKey("par_budget_analysis.id"), nullable=False
    )

    ce = Column(Float, nullable=True)
    construction = Column(Float, nullable=True)
    feasibility_studies = Column(Float, nullable=True)
    design = Column(Float, nullable=True)
    rights_of_way = Column(Float, nullable=True)
    equipment = Column(Float, nullable=True)

    # relationship
    federal_fund = relationship("FederalFund", back_populates="additional_fund")
    par_budget_analysis = relationship(
        "ParBudgetAnalysis", back_populates="additional_fund"
    )

    eagers = ["federal_fund", "par_budget_analysis"]
