from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class ParActivity(BaseModel):
    __tablename__ = "par_activity"

    par_id = Column(Integer, ForeignKey("par.id"), nullable=False)
    activity = Column(String, nullable=True)
    status = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    user = Column(String, nullable=True)
    comments = Column(String, nullable=True)

    par = relationship("Par", back_populates="par_activities")
