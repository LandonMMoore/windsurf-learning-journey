from typing import Dict, Literal, Optional

from abs_nosql_repository_core.document import BaseDocument

from src.mongodb.collections import (
    FORMULA_ASSISTANT_CHAT_HISTORY_COLLECTION,
    REPORT_CHAT_HISTORY_COLLECTION,
)


class BaseChatHistory(BaseDocument):
    user_id: int
    chat_id: int
    user_query: str
    response: str
    message_id: Optional[int] = 1


class ReportChatHistory(BaseChatHistory):
    feedback: Optional[Literal["like", "dislike", "null"]] = None
    class Settings:
        name = REPORT_CHAT_HISTORY_COLLECTION
        indexes = ["user_id", [("user_id", 1), ("chat_id", -1), ("message_id", -1)]]


class FormulaAssistantChatHistory(BaseChatHistory):
    sub_report_id: Optional[int] = None
    user_id: int
    chat_id: int
    user_query: str
    response: Optional[dict] = None
    message_id: Optional[int] = 1

    class Settings:
        name = FORMULA_ASSISTANT_CHAT_HISTORY_COLLECTION
        indexes = ["user_id", [("user_id", 1), ("chat_id", -1), ("message_id", -1)]]
