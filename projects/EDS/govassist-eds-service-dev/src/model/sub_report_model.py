from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class SubReport(BaseModel):
    __tablename__ = "eds_sub_report_configurations"
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=False)
    index_name = Column(String(100), nullable=False, unique=True)
    report_configuration_id = Column(
        Integer, ForeignKey("eds_report_configurations.id"), nullable=False
    )
    report_configuration = relationship(
        "ReportConfiguration", back_populates="sub_reports"
    )
    workflows = relationship("SubReportWorkflow", back_populates="sub_report")


class SubReportWorkflow(BaseModel):
    __tablename__ = "eds_sub_report_workflows"
    sub_report_id = Column(
        Integer,
        ForeignKey("eds_sub_report_configurations.id", ondelete="CASCADE"),
        nullable=False,
    )
    # PENDING, IN_PROGRESS, COMPLETED, FAILED
    status = Column(String(50), nullable=True, default="PENDING")
    error_log = Column(Text, nullable=True)
    execution_success_time = Column(DateTime, nullable=True)

    sub_report = relationship("SubReport", back_populates="workflows")
