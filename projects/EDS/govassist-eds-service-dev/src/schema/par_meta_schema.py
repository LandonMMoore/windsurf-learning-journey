from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ParMeta(BaseModel):
    epar_name: str
    request_type: Optional[str] = None
    total_project_budget: Optional[float] = None
    project_name: Optional[str] = None
    funding_source: Optional[str] = None
    icrs_exempt: Optional[bool] = None
    icrs_rate: Optional[float] = None
    project_details_id: Optional[int] = None
    current_status: Optional[str] = None
    user: Optional[str] = None
    updated_date: Optional[datetime] = None


class ParMetaUpdate(BaseModel):
    icrs_exempt: Optional[bool] = None
    icrs_rate: Optional[float] = None
