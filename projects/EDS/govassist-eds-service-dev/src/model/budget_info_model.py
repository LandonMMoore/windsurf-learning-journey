from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class BudgetInfo(BaseModel):
    __tablename__ = "budget_info"
    par_id = Column(Integer, ForeignKey("par.id"), nullable=False)
    task_name = Column(String, nullable=True)

    par = relationship("Par", back_populates="budget_info")
    budget_items = relationship("BudgetItems", back_populates="budget_info")

    eagers = ["budget_items"]
