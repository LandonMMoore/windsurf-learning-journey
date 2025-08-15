from sqlalchemy import JSON, Column, String

from src.model.base_model import BaseModel


class WorkflowStatus(BaseModel):
    __tablename__ = "workflow_status"

    description = Column(String, nullable=True)
    state_code = Column(String, nullable=False)
    state_metadata = Column(JSON, nullable=False)
    next_state_codes = Column(JSON, nullable=False)
    notify_roles = Column(JSON, nullable=False)

    # can_view = Column(Boolean, nullable=False, default=False)
    # can_edit = Column(Boolean, nullable=False, default=False)
