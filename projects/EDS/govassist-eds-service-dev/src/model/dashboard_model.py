import enum

from abs_auth_rbac_core.models import Users
from sqlalchemy import JSON, Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class VisibilityType(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"


class Dashboard(BaseModel):
    __tablename__ = "dashboard"
    name = Column(String)
    description = Column(String)
    created_by = Column(Integer)
    visibility = Column(Enum(VisibilityType), default=VisibilityType.PRIVATE)
    auto_refresh = Column(Boolean, default=False)
    filters = Column(JSON, nullable=True, default=None)

    created_by_user = relationship(
        Users,
        primaryjoin=lambda: Dashboard.created_by == Users.id,
        foreign_keys=[created_by],
        viewonly=True,
    )

    dashboard_widgets = relationship(
        "DashboardWidget",
        back_populates="dashboard",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    favorites = relationship(
        "DashboardFavorite",
        back_populates="dashboard",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    shared_with = relationship(
        "DashboardShare",
        back_populates="dashboard",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    eagers = ["dashboard_widgets", "shared_with", "favorites", "created_by_user"]
