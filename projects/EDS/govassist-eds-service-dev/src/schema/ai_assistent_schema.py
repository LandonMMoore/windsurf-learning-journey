import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, validator


class ChatRequest(BaseModel):
    query: str
    chat_id: Optional[int] = 0
    parent_id: Optional[int] = 0


class ValidateQuery(ChatRequest):
    user_id: int

    @validator("query")
    def validate_query(cls, v):
        if len(v) > 250:
            raise ValueError(
                "Input query is too long, it must be less than 250 characters"
            )

        combined_pattern = re.compile(
            r"(system:|assistant:|user:|role:|content:|"
            r"ignore previous|ignore above|forget everything|"
            r"you are now|act as|pretend to be|"
            r"_source|_index|_id|_score|_shards|"
            r"settings|mappings|analyzer|tokenizer|"
            r"provide\s+(the\s+)?credentials|"
            r"(access|admin|login|password|username)\s+(to|for)\s+(your\s+)?(database|system|account)|"
            r"give\s+me\s+access|"
            r"bypass\s+(authentication|security|rules|restrictions|limitations)|"
            r"disable\s+security|"
            r"auth\s*token|api[_-]?key|secret[_-]?key|authorization\s*header|"
            r"follow\s+my\s+orders|"
            r"do\s+not\s+consider\s+(any\s+)?rules|"
            r"strictly\s+bypass|"
            r"ignore\s+(all\s+)?(rules|restrictions|limitations))",
            re.IGNORECASE,
        )

        if combined_pattern.search(v):
            logger.warning(f"Query contains potentially malicious content: {v}")
            raise ValueError("Query contains potentially malicious content")

        return v.strip()


class ChatResponse(BaseModel):
    response: str
    chat_id: int
    message_id: int
    parent_message_id: Optional[int]


class ChatHistoryResponse(BaseModel):
    id: int
    title: str
    updated_at: datetime


class PaginatedChatHistoryResponse(BaseModel):
    items: List[ChatHistoryResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class ChatMessagesResponse(BaseModel):
    eds_chat_history_id: str
    messages: List[Dict[str, Any]]
