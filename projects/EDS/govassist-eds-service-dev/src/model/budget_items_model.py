from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class BudgetItems(BaseModel):
    __tablename__ = "budget_items"

    account = Column(String, nullable=False)
    parent_task_number = Column(String, nullable=True)
    parent_task_name = Column(String, nullable=True)
    subtask_number = Column(String, nullable=True)
    lifetime_budget = Column(Float, nullable=True)
    initial_allotment = Column(Float, nullable=True)
    expenditures = Column(Float, nullable=True)
    obligations = Column(Float, nullable=True)
    commitments = Column(Float, nullable=True)
    current_balance = Column(Float, nullable=True)
    lifetime_balance = Column(Float, nullable=True)
    proposed_budget = Column(Float, nullable=True)
    change_amount = Column(Float, nullable=True)
    budget_info_id = Column(Integer, ForeignKey("budget_info.id"), nullable=False)
    comment = Column(String, nullable=True)

    budget_info = relationship("BudgetInfo", back_populates="budget_items")
