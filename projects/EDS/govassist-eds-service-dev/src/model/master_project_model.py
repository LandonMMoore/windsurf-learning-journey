from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class MasterProject(BaseModel):
    __tablename__ = "master_project"
    master_project_number = Column(Integer, nullable=False)
    master_project_name = Column(String, nullable=True)

    project_details = relationship("ProjectDetails", back_populates="master_project")
