from typing import Annotated, Optional, TypedDict

from langgraph.graph import add_messages

from src.mongodb.collections import EDSAssistanceLog


class State(TypedDict):
    messages: Annotated[list, add_messages]
    summary: Optional[str]
    chat_history: Optional[list[dict]]
    log: Optional[EDSAssistanceLog]
    user_id: Optional[str]
    user_query: Optional[str]
