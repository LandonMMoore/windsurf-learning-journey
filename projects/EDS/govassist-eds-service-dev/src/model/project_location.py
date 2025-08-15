from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class ProjectLocation(BaseModel):
    __tablename__ = "project_location"
    location = Column(String, nullable=False)

    project_details = relationship("ProjectDetails", back_populates="project_location")
