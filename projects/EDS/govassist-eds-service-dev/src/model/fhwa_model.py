from sqlalchemy import Column, String

from src.model.base_model import BaseModel


class Fhwa(BaseModel):
    __tablename__ = "fhwa"
    program_code = Column(String, nullable=True)
    project_number = Column(String, nullable=True)
    soar_grant = Column(String, nullable=True)
    soar_project_no = Column(String(50), nullable=True)
    stip_reference = Column(String, nullable=True)
    categories = Column(String(50), nullable=True)
