from sqlalchemy import Column, Float, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class FederalFund(BaseModel):
    __tablename__ = "federal_fund"
    fund_code = Column(String, nullable=False)
    fund_available = Column(Float, nullable=False)
    fund_obligations = Column(Float, nullable=False)
    fund_unobligated_balance = Column(Float, nullable=False)
    fund_pending_obligations = Column(Float, nullable=False)
    fund_pending_unobligated_balance = Column(Float, nullable=False)
    fund_advance_construction = Column(Float, nullable=False)
    additional_fund = relationship("AdditionalFund", back_populates="federal_fund")
    par_budget_analysis_fund = relationship(
        "ParBudgetAnalysisFund", back_populates="federal_fund"
    )
