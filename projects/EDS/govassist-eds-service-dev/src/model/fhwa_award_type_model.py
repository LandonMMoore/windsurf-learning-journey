from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class FhwaAwardType(BaseModel):
    __tablename__ = "fhwa_award_type"

    code = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # Relationships
    par_award_associations = relationship(
        "ParAwardAssociation", back_populates="award_type"
    )
