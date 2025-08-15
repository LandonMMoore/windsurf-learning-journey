from abs_auth_rbac_core.models import Users
from sqlalchemy import Column, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class DashboardFavorite(BaseModel):
    __tablename__ = "dashboard_favorites"

    user_id = Column(Integer, nullable=False)
    dashboard_id = Column(
        Integer, ForeignKey("dashboard.id", ondelete="CASCADE"), nullable=False
    )

    user = relationship(
        Users,
        primaryjoin=lambda: DashboardFavorite.user_id == Users.id,
        foreign_keys=[user_id],
        viewonly=True,
    )

    dashboard = relationship("Dashboard", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "dashboard_id", name="uix_user_dashboard"),
        Index("ix_dashboard_favorites_user_id", "user_id"),
        Index("ix_dashboard_favorites_dashboard_id", "dashboard_id"),
    )

    eagers = ["dashboard", "dashboard.created_by_user"]
