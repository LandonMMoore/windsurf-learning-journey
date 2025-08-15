from sqlalchemy import Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class DashboardShare(BaseModel):
    __tablename__ = "dashboard_share"

    dashboard_id = Column(
        Integer, ForeignKey("dashboard.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, nullable=False)
    email = Column(String(255), nullable=True)

    # Relationships
    dashboard = relationship("Dashboard", back_populates="shared_with", lazy="joined")

    __table_args__ = (
        UniqueConstraint("dashboard_id", "user_id", name="uix_dashboard_user"),
        Index("ix_dashboard_share_dashboard_id", "dashboard_id"),
        Index("ix_dashboard_share_user_id", "user_id"),
    )
