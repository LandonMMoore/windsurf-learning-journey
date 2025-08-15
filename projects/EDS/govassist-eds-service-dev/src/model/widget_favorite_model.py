from abs_auth_rbac_core.models import Users
from sqlalchemy import Column, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class WidgetFavorite(BaseModel):
    __tablename__ = "widget_favorites"

    user_id = Column(Integer, nullable=False)
    widget_id = Column(Integer, ForeignKey("dashboard_widget.id"), nullable=False)

    # Relationships
    user = relationship(
        Users,
        primaryjoin=lambda: WidgetFavorite.user_id == Users.id,
        foreign_keys=[user_id],
        viewonly=True,
    )
    widget = relationship("DashboardWidget", back_populates="favorites")

    # Unique constraint to prevent duplicate favorites
    __table_args__ = (
        UniqueConstraint("user_id", "widget_id", name="uix_user_widget"),
        Index("ix_widget_favorites_user_id", "user_id"),
        Index("ix_widget_favorites_widget_id", "widget_id"),
    )

    eagers = ["widget"]
