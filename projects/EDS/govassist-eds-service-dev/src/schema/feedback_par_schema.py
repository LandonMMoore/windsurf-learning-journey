from typing import List, Literal, Optional

from pydantic import BaseModel


class ImagePayload(BaseModel):
    name: str
    base64: str  # base64 string


class FeedbackPayload(BaseModel):
    page_name: Literal[
        "PAR",
        "PAR_DASHBOARD",
        "AI_DETERMINATION",
        "GENERAL_INFORMATION",
        "PROJECT_DETAILS",
        "BUDGET",
        "REVIEW",
        "DEMO_CONTROL_PANEL",
        "DASHBOARDS",
        "EDS_ASSISTANT",
        "REPORTS",
    ]
    issue_type: Literal[
        "NEW_FIELD_REQUEST",
        "NEW_FORMULA",
        "NEW_FORMAT",
        "NEW_WORKFLOW",
        "SOMETHING_ELSE",
    ]
    description: str
    images: Optional[List[ImagePayload]] = None
