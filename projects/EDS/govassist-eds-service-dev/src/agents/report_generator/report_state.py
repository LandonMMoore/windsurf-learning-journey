from typing import NotRequired, Optional, Union

from langgraph.prebuilt.chat_agent_executor import AgentState
from pydantic import BaseModel, Field


class ReportAgentState(AgentState):
    chat_id: NotRequired[Union[str, None]] = Field(default=None)
    report_id: NotRequired[Union[int, None]] = Field(default=None)
    report_name: NotRequired[Union[str, None]] = Field(default=None)
    report_description: NotRequired[Union[str, None]] = Field(default=None)
    report_tags: NotRequired[Union[list[str], None]] = Field(default_factory=list)
    report_schedule: NotRequired[Union[str, None]] = Field(default=None)
    report_configs: NotRequired[Union[list[dict], None]] = Field(default_factory=list)
    is_last_step: NotRequired[Union[bool, None]] = Field(default=False)
    remaining_steps: NotRequired[Union[int, None]] = Field(default=0)


class ReportAgentStateSchema(BaseModel):
    chat_id: Optional[Union[str, None]] = Field(
        default=None, description="The ID of the chat session"
    )
    report_id: Optional[Union[int, None]] = Field(
        default=None, description="The ID of the report"
    )
    report_name: Optional[Union[str, None]] = Field(
        default=None, description="The name of the report"
    )
    report_description: Optional[Union[str, None]] = Field(
        default=None, description="The description of the report"
    )
    report_tags: Optional[Union[list[str], None]] = Field(
        default=None, description="The tags of the report"
    )
    report_schedule: Optional[Union[str, None]] = Field(
        default=None, description="The schedule of the report"
    )
    report_configs: Optional[Union[list[dict], None]] = Field(
        default=None, description="The configs of the report"
    )


class UpdateAgentStateSchema(BaseModel):
    new_state: ReportAgentStateSchema
