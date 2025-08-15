from abs_auth_rbac_core.models.user import Users
from sqlalchemy import JSON, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class EdsIntegration(BaseModel):
    __tablename__ = "eds_integrations"
    __table_args__ = {"extend_existing": True}

    integration_id = Column(String, nullable=False, unique=True)
    integration_uuid = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    folder_id = Column(String, nullable=False)
    folder_name = Column(String, nullable=False)
    site_id = Column(String, nullable=False)
    path = Column(String, nullable=False)
    list_id = Column(String, nullable=False)
    drive_id = Column(String, nullable=False)
    webhook_info = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    workflows = relationship("EdsWorkflow", back_populates="integration")

    eagers = []

    user = relationship(
        Users,
        primaryjoin=lambda: EdsIntegration.user_id == Users.id,
        foreign_keys=[user_id],
        backref="integrations",
        viewonly=True,
    )
