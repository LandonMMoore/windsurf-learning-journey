from sqlalchemy import Column, DateTime, String

from src.model.base_model import BaseModel


class ReportMetadata(BaseModel):
    __tablename__ = "report_metadata"
    report_id = Column(String, nullable=False)
    index_name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    report_name = Column(String, nullable=False)
    report_description = Column(String, nullable=False)
    report_last_synced_at = Column(DateTime, nullable=False)
    usage_tags = Column(String, nullable=False)
