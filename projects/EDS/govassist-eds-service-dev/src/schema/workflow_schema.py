from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.schema.base_schema import FindBase, FindResult, SearchOptions, make_optional
from src.schema.integration_schema import IntegrationBase


class ExcelSheetName(str, Enum):
    COA_MASTER_DATA = "CoA Master Data"
    AWARD_PROJECT_MASTER_DATA = "Award & Project Master Data"
    SUMMARY_BALANCES = "Summary Balances"
    TRANSACTIONAL_DETAIL_DATA = "Transactional Detail Data"


class WorkflowStatusEnum(Enum):
    INITIATED = "Initiated"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class WorkflowTypeEnum(Enum):
    MANUAL = "Manual"
    AUTOMATED = "Automated"


class WorkflowStepEnum(str, Enum):
    INITIALIZATION = "Initialization"
    DOWNLOAD = "Download"
    VALIDATION = "Validation"
    PROCESSING = "Processing"
    COMPLETION = "Completion"
    ERROR = "Error"


class WorkflowStepStatusEnum(Enum):
    STARTED = "Started"
    COMPLETED = "Completed"
    FAILED = "Failed"


# Workflow Schema for Webhook and Celery Task Operations
class WorkflowStatus(str, Enum):
    """Workflow execution statuses"""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileProcessingStatus(str, Enum):
    """Individual file processing statuses"""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class FolderType(str, Enum):
    """Folder types"""

    DAILY = "daily"
    WEEKLY = "weekly"


class LogLevel(str, Enum):
    """Log levels for workflow logging"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class WorkflowLogEntry(BaseModel):
    """Individual log entry"""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: LogLevel
    message: str
    file_name: Optional[str] = None
    step: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class WorkflowProgressCreate(WorkflowLogEntry):
    workflow_id: int


class FileProcessingInfo(BaseModel):
    """Individual file processing information"""

    file_id: Optional[str] = None
    file_name: Optional[str] = None
    download_url: Optional[str] = None
    status: FileProcessingStatus = FileProcessingStatus.PENDING
    progress_percentage: float = 0.0
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    invalid_rows_count: int = 0
    valid_rows_count: int = 0
    total_rows: int = 0
    processed_at: Optional[str] = None
    error_messages: List[str] = Field(default_factory=list)


class WorkflowState(BaseModel):
    """Complete workflow state"""

    workflow_id: str
    task_id: Optional[str] = None
    drive_id: str
    folder_id: str
    folder_name: str
    folder_type: FolderType
    status: WorkflowStatus = WorkflowStatus.PENDING
    progress_percentage: float = 0.0

    # File tracking
    total_files: int = 0
    files_processed: int = 0
    files_failed: int = 0
    files: Dict[str, FileProcessingInfo] = Field(default_factory=dict)

    # Timestamps
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Results
    total_rows_processed: int = 0
    total_invalid_rows: int = 0
    output_files: List[str] = Field(default_factory=list)

    # Error handling
    error_messages: List[str] = Field(default_factory=list)
    retry_count: int = 0

    # Logs (stored separately but referenced here)
    log_count: int = 0


class WorkflowStateUpdate(make_optional(WorkflowState)):
    pass


class FolderProcessingContext(BaseModel):
    drive_id: str
    folder_id: str
    folder_type: FolderType = FolderType.DAILY
    integration_id: int
    folder_name: str = "unknown"
    processed_folder_id: str


# Workflow Schema for CRUD Operations
class WorkflowBase(BaseModel):
    integration_id: Optional[int] = None
    drive_id: Optional[str] = None
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    status: Optional[WorkflowStatusEnum] = None
    type: Optional[WorkflowTypeEnum] = None
    is_active: Optional[bool] = None
    workflow_created_at: Optional[datetime] = None
    workflow_started_at: Optional[datetime] = None
    workflow_completed_at: Optional[datetime] = None
    error_messages: Optional[List[str]] = []
    progress_percentage: Optional[float] = None
    total_files: Optional[int] = None
    files_processed: Optional[int] = None
    files_failed: Optional[int] = None


class WorkflowCreate(WorkflowBase):
    drive_id: str
    folder_id: str
    processed_folder_id: str


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowFind(make_optional(FindBase), make_optional(WorkflowBase)):
    pass


class WorkflowProgressInfo(BaseModel):
    id: int
    workflow_id: int
    step: WorkflowStepEnum
    status: Optional[WorkflowStepStatusEnum] = None
    message: Optional[str] = None
    file_name: Optional[str] = None
    timestamp: datetime


class WorkflowInfo(WorkflowBase):
    id: int
    is_active: bool
    progress_records: Optional[List[WorkflowProgressInfo]] = None
    integration: Optional[IntegrationBase] = None


class WorkflowListResponse(FindResult):
    founds: Optional[List[WorkflowInfo]] = None
    search_options: Optional[SearchOptions] = None
