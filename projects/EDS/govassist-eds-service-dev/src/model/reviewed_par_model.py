import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Index, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ReviewedPar(Base):
    __tablename__ = "reviewed_par"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    par_id = Column(String(50), nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)

    __table_args__ = (Index("idx_user_par", "user_id", "par_id"),)
