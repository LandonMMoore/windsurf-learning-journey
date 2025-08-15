from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class Organization(BaseModel):
    __tablename__ = "eds_organization"
    project_organization = Column(String, nullable=False)

    project_details = relationship("ProjectDetails", back_populates="organization")
