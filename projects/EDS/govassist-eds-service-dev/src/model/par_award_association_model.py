from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class ParAwardAssociation(BaseModel):
    __tablename__ = "par_award_association"
    __table_args__ = (
        UniqueConstraint(
            "project_details_id", "award_type_id", name="uix_project_details_award_type"
        ),
    )

    project_details_id = Column(
        Integer, ForeignKey("project_details.id"), nullable=False
    )
    award_type_id = Column(Integer, ForeignKey("fhwa_award_type.id"), nullable=False)

    # Relationships
    project_details = relationship(
        "ProjectDetails", back_populates="par_award_associations"
    )
    award_type = relationship("FhwaAwardType", back_populates="par_award_associations")

    eagers = ["award_type"]
