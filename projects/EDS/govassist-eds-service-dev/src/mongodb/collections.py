from datetime import UTC, datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: int = Field(default_factory=lambda: 0)  # Will be auto-incremented
    query: str
    response: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    parent_message_id: Optional[int] = 0


class ChatMessage(BaseModel):
    id: int = Field(default_factory=lambda: 0)  # Will be auto-incremented
    eds_chat_history_id: str
    messages: List[Message] = Field(default_factory=list)


class EDSChatHistory(BaseModel):
    id: int = Field(default_factory=lambda: 0)  # Will be auto-incremented
    userid: str
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReportGenerationStep(str, Enum):
    """Steps in the report generation process"""

    UNDERSTANDING_REQUIREMENTS = "understanding_requirements"
    # ANALYZING_FIELDS = "analyzing_fields"
    CLARIFYING_QUESTIONS = "clarifying_questions"
    FIELD_AND_CALCULATION_ANALYSIS = "field_and_calculation_analysis"
    REPORT_GENERATION = "report_generation"
    REPORT_GENERATION_COMPLETED = "report_generation_completed"
    REPORT_GENERATION_FAILED = "report_generation_failed"


class ReportGeneration(BaseModel):
    """Model for tracking report generation process"""

    id: int = Field(default_factory=lambda: 0)  # Will be auto-incremented
    chat_id: int
    userid: str
    current_step: ReportGenerationStep = Field(
        default=ReportGenerationStep.UNDERSTANDING_REQUIREMENTS
    )

    # Initial request and understanding
    final_requirements_summary: str

    # Field analysis
    selected_fields: List[Dict] = Field(default_factory=list)

    # Clarifying questions
    clarifying_questions: List[Dict] = Field(default_factory=list)
    additional_sections: List[Dict] = Field(default_factory=list)

    # Calculation methods
    calculation_methods: List[Dict] = Field(default_factory=list)

    # Report details
    report_type: str
    time_period: Optional[Dict] = None
    data_sources: List[str] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None


# MongoDB collection names
EDS_CHAT_HISTORY_COLLECTION = "eds_chat_history"
EDS_REPORT_CHAT_HISTORY_COLLECTION = "eds_report_chat_history"
CHAT_MESSAGES_COLLECTION = "chat_messages"
CHAT_MESSAGES_REPORT_COLLECTION = "chat_messages_report"

# eds_report collection is used to store the report config in V2 version of the report generation
REPORT_COLLECTION = "eds_report"
# eds_report_chat_history collection is used to store the report chat history in V2 version of the report generation
REPORT_CHAT_HISTORY_COLLECTION = "eds_report_chat_history"
FORMULA_ASSISTANT_CHAT_HISTORY_COLLECTION = "eds_formula_assistant_chat_history"


# EDS Assistance Log
EDS_ASSISTANCE_LOG_COLLECTION = "eds_assistance_log"


class EDSAssistanceStatus(str, Enum):
    """Status of EDS assistance processing"""

    SUCCESS = "success"
    FAILED = "failed"
    PROCESSING = "processing"
    MALICIOUS = "malicious"
    QUERY_GENERATION_FAILED = "query_generation_failed"
    QUERY_EXECUTION_FAILED = "query_execution_failed"
    QUERY_SUMMARIZATION_FAILED = "query_summarization_failed"
    QUERY_EXECUTION_SUCCESS = "query_execution_success"
    QUERY_SUMMARIZATION_SUCCESS = "query_summarization_success"
    QUERY_GENERATION_SUCCESS = "query_generation_success"
    RESPONSE_SANITIZATION_SUCCESS = "response_sanitization_success"


class EDSAssistanceLog(BaseModel):
    user_query: str
    user_id: str
    chat_id: Optional[int] = None
    parent_message_id: Optional[int] = None
    metadata: Optional[Dict] = None
    status: Optional[EDSAssistanceStatus] = None
    malicious_content: Optional[str] = None
    error_message: Optional[str] = None
    processing_latency_s_query: Optional[float] = None
    processing_latency_s_summarizer: Optional[float] = None
    processing_latency_s_executor: Optional[float] = None
    total_processing_latency_s: Optional[float] = None
    generated_es_query: Optional[Dict] = None
    generated_es_response: Optional[Dict] = None
    response_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
