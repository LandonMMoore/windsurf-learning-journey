from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel
from src.schema.workflow_schema import (
    FolderType,
    WorkflowStatusEnum,
    WorkflowStepEnum,
    WorkflowStepStatusEnum,
    WorkflowTypeEnum,
)


class EdsWorkflow(BaseModel):
    __tablename__ = "eds_workflow"
    __table_args__ = {"extend_existing": True}

    task_id = Column(String, nullable=True)
    processed_folder_id = Column(String, nullable=False)
    integration_id = Column(Integer, ForeignKey("eds_integrations.id"), nullable=True)
    drive_id = Column(String, nullable=False)
    folder_id = Column(String, nullable=False)
    folder_name = Column(String, nullable=False)
    folder_type = Column(Enum(FolderType), nullable=False, default=FolderType.DAILY)

    status = Column(
        Enum(WorkflowStatusEnum), nullable=False, default=WorkflowStatusEnum.INITIATED
    )
    type = Column(
        Enum(WorkflowTypeEnum), nullable=False, default=WorkflowTypeEnum.AUTOMATED
    )

    progress_percentage = Column(Float, default=0.0)
    total_files = Column(Integer, default=0)
    files_processed = Column(Integer, default=0)
    files_failed = Column(Integer, default=0)

    workflow_created_at = Column(DateTime, default=datetime.now(UTC), nullable=True)
    workflow_started_at = Column(DateTime, nullable=True)
    workflow_completed_at = Column(DateTime, nullable=True)

    error_messages = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    integration = relationship("EdsIntegration", back_populates="workflows")
    progress_records = relationship(
        "EdsWorkflowProgress", back_populates="workflow", cascade="all, delete-orphan"
    )

    eagers = ["progress_records", "integration"]


class EdsWorkflowProgress(BaseModel):
    __tablename__ = "eds_workflow_progress"
    __table_args__ = {"extend_existing": True}

    workflow_id = Column(Integer, ForeignKey("eds_workflow.id"), nullable=False)
    step = Column(Enum(WorkflowStepEnum), nullable=False)
    status = Column(Enum(WorkflowStepStatusEnum), nullable=True)
    message = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))

    workflow = relationship("EdsWorkflow", back_populates="progress_records")
