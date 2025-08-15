from enum import Enum

from abs_auth_rbac_core.models import Users
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from src.model.base_model import Base, BaseModel


class ScheduleReportRerunPeriod(Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    QUARTERLY = "QUARTERLY"


class ReportConfiguration(BaseModel):
    __tablename__ = "eds_report_configurations"
    __table_args__ = {"extend_existing": True}

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_by_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    created_by = relationship(Users, foreign_keys=[created_by_id])
    last_synced_at = Column(DateTime, nullable=True)
    schedule_rerun_period = Column(String, nullable=True)
    chat_id = Column(Integer, nullable=True)
    template_id = Column(Integer, ForeignKey("eds_report_templates.id"), nullable=True)
    template = relationship("ReportTemplate", backref="report_configurations")
    chat_id = Column(Integer, nullable=True)
    tags_association = relationship(
        "ReportConfigurationTagAssociation",
        back_populates="report_configuration",
    )
    sub_reports = relationship("SubReport", back_populates="report_configuration")

    @hybrid_property
    def tags(self):
        return [tag.tag for tag in self.tags_association]

    eagers = ["tags_association", "tags_association.tag", "sub_reports"]


class Tag(BaseModel):
    __tablename__ = "eds_tags"
    __table_args__ = {"extend_existing": True}

    name = Column(String, nullable=False, unique=True)
    report_configurations = relationship(
        "ReportConfigurationTagAssociation", back_populates="tag"
    )
    report_templates = relationship(
        "ReportTemplateTagAssociation", back_populates="tag"
    )


class ReportConfigurationTagAssociation(Base):
    __tablename__ = "eds_report_configuration_tag_associations"
    __table_args__ = (
        UniqueConstraint("report_configuration_id", "tag_id"),
        PrimaryKeyConstraint("report_configuration_id", "tag_id"),
        {"extend_existing": True},
    )

    report_configuration_id = Column(
        Integer, ForeignKey(ReportConfiguration.id), nullable=False
    )
    tag_id = Column(Integer, ForeignKey(Tag.id), nullable=False)

    report_configuration = relationship(
        ReportConfiguration, back_populates="tags_association"
    )
    tag = relationship(Tag, back_populates="report_configurations")


class ReportTemplateTagAssociation(Base):
    __tablename__ = "eds_report_template_tag_associations"
    __table_args__ = (
        UniqueConstraint("report_template_id", "tag_id"),
        PrimaryKeyConstraint("report_template_id", "tag_id"),
        {"extend_existing": True},
    )

    report_template_id = Column(
        Integer, ForeignKey("eds_report_templates.id"), nullable=False
    )
    tag_id = Column(Integer, ForeignKey(Tag.id), nullable=False)

    report_template = relationship("ReportTemplate", back_populates="tags_association")
    tag = relationship(Tag, back_populates="report_templates")


class ReportTemplate(BaseModel):
    __tablename__ = "eds_report_templates"
    __table_args__ = {"extend_existing": True}

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=False)
    created_by_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    created_by = relationship(Users, foreign_keys=[created_by_id])
    is_predefined = Column(Boolean, nullable=False, default=False)
    tags_association = relationship(
        "ReportTemplateTagAssociation",
        back_populates="report_template",
    )

    @hybrid_property
    def tags(self):
        return [tag.tag for tag in self.tags_association]

    eagers = ["tags_association", "tags_association.tag"]


class ReportExport(BaseModel):
    __tablename__ = "eds_report_exports"

    report_id = Column(
        Integer, ForeignKey("eds_report_configurations.id"), nullable=False
    )
    report = relationship("ReportConfiguration", backref="exports")

    # PENDING, IN_PROGRESS, COMPLETED, FAILED
    status = Column(String, default="PENDING")
    file_name = Column(String, nullable=True)
    error_message = Column(String, nullable=True)

    # If the export is completed and after export the report is updated, then the export is stale.
    stale_at = Column(DateTime, nullable=True)

    created_by_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    created_by = relationship(Users, foreign_keys=[created_by_id])
