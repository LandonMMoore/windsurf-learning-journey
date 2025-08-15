from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from src.schema.base_schema import (
    FindBase,
    FindResult,
    ModelBaseInfo,
    SearchOptions,
    make_optional,
)


class ReportMetadataBase(BaseModel):
    report_id: Optional[str] = None
    index_name: Optional[str] = None
    display_name: Optional[str] = None
    report_name: Optional[str] = None
    report_description: Optional[str] = None
    report_last_synced_at: Optional[datetime] = None


class ReportMetadataInfo(ModelBaseInfo, ReportMetadataBase):
    pass


class UsageTags(str, Enum):
    DASHBOARD = "dashboard"
    ASSISTANT = "assistance"


class ReportMetadataFind(make_optional(FindBase), make_optional(ReportMetadataBase)):
    usage_tags: Optional[UsageTags] = UsageTags.DASHBOARD
    pass


class ReportMetadataListResponse(FindResult):
    founds: Optional[List[ReportMetadataInfo]] = None
    search_options: Optional[SearchOptions] = None
