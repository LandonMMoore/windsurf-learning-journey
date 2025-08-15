from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class Award(BaseModel):
    __tablename__ = "award"
    sponsor = Column(String, nullable=True)
    award_name = Column(String, nullable=True)

    project_details = relationship("ProjectDetails", back_populates="award")
