from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class CostCenter(BaseModel):
    __tablename__ = "cost_center"
    cost_center = Column(String, nullable=True)
    cost_center_name = Column(String, nullable=True)
    cost_center_parent1 = Column(String, nullable=True)
    cost_center_parent1_desc = Column(String, nullable=True)

    project_details = relationship("ProjectDetails", back_populates="cost_center")
