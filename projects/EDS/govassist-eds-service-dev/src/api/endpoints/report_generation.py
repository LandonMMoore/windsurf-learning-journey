from datetime import datetime
from typing import Dict, Optional

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel

from src.agents.analyzer_agent import process_requirements_summary
from src.agents.clarify_agent import clarify_question_agent
from src.agents.report_generation_manager_agent import ReportGenerationManagerAgent
from src.core.dependencies import get_current_user
from src.core.exceptions import InternalServerError, NotFoundError
from src.mongodb.chat_services import (
    clear_chat_messages,
    get_chat_messages,
    get_eds_chat_history,
)
from src.mongodb.collections import (
    CHAT_MESSAGES_REPORT_COLLECTION,
    EDS_REPORT_CHAT_HISTORY_COLLECTION,
    Message,
    ReportGenerationStep,
)
from src.mongodb.report_services import (
    get_report,
    update_calculation_methods,
    update_report_step,
    update_requirement_summary,
    update_selected_fields,
)

router = APIRouter(prefix="/report", tags=["Report Generation"], deprecated=True)

# Initialize the agent
report_agent = ReportGenerationManagerAgent()


class ChatRequest(BaseModel):
    query: str
    chat_id: Optional[int] = None
    parent_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    chat_id: int
    message_id: int
    parent_message_id: int
    has_final_summary: bool = False


class ConfirmRequirementsRequest(BaseModel):
    chat_id: int


class FieldsUpdateRequest(BaseModel):
    chat_id: int
    fields: list[Dict]


class FieldAnalyzerRequest(BaseModel):
    chat_id: int


class FieldAnalyzerResponse(BaseModel):
    data_sources_status: bool
    data_structure_status: bool
    assessing_data_quality_status: bool


class CalculationMethodsRequest(BaseModel):
    chat_id: int
    methods: list[Dict]


class ProcessPromptRequest(BaseModel):
    prompt: str
    chat_id: Optional[int] = None


class UpdateReportStepRequest(BaseModel):
    chat_id: int
    step: ReportGenerationStep


class ClarifyAgentRequest(BaseModel):
    query: str = None
    chat_id: int
    parent_id: int = None
    additional_section: bool = False


class ClarifyAgentResponse(BaseModel):
    chat_id: int
    clarifying_questions: list[Message] = []
    additional_sections: list[Message] = []


class RegenerateDescribeChatRequest(BaseModel):
    query: str
    chat_id: int
    message_id: int
    parent_message_id: int


class DescribeChatHistoryResponse(BaseModel):
    chat_id: int
    messages: list[Message]
    has_final_summary: bool = False


@router.post("/chat", response_model=ChatResponse)
@inject
async def chat_with_agent(
    data: ChatRequest, current_user: dict = Depends(get_current_user)
):
    """
    Chat with the report generation agent to gather and understand requirements.
    """
    try:
        response = await report_agent.process_query(
            query=data.query,
            userid=str(current_user.id),
            chat_id=data.chat_id,
            parent_message_id=data.parent_id,
        )

        return ChatResponse(**response)
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Error in chat_with_agent for user {current_user.id}")
        raise InternalServerError(detail="Internal Server Error")


@router.post("/confirm-requirements")
@inject
async def confirm_requirements(
    data: ConfirmRequirementsRequest, current_user: dict = Depends(get_current_user)
):
    """
    Confirm the gathered requirements and move to the next phase.
    """
    try:
        # Get the current report
        report = await get_report(data.chat_id, str(current_user.id))
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        logger.info("Requirements summary : ", report.get("requirements_summary"))

        if report.get("requirements_summary") is None:
            raise HTTPException(
                status_code=400,
                detail="Requirements summary is not confirmed. Please confirm the requirements summary first.",
            )

        # Update the report status and save the final requirements
        updated_report = await update_report_step(
            chat_id=data.chat_id,
            step=ReportGenerationStep.FIELD_AND_CALCULATION_ANALYSIS,
            additional_data={
                "final_requirements_summary": report.get("requirements_summary", ""),
                "requirements_confirmed_at": datetime.utcnow(),
            },
        )

        # Convert ObjectId to string in the response
        response_data = {
            "status": "success",
            "message": "Requirements confirmed successfully",
            "next_step": ReportGenerationStep.FIELD_AND_CALCULATION_ANALYSIS,
            "report": {},
        }

        # Convert the report to a dictionary and handle ObjectId
        if updated_report:
            report_dict = dict(updated_report)
            if "_id" in report_dict:
                report_dict["_id"] = str(report_dict["_id"])
            response_data["report"] = report_dict

        return response_data
    except HTTPException:
        raise
    except Exception:
        raise InternalServerError(detail="Internal Server Error")


@router.post("/update-fields")
@inject
async def update_report_fields(
    data: FieldsUpdateRequest, current_user: dict = Depends(get_current_user)
):
    """
    Update the selected fields for the report.
    """
    try:
        report = await get_report(data.chat_id, str(current_user.id))
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        updated_report = await update_selected_fields(
            chat_id=data.chat_id, fields=data.fields
        )

        return {
            "status": "success",
            "message": "Fields updated successfully",
            "report": updated_report,
        }
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Error updating fields for user {current_user.id}")
        raise InternalServerError(detail="Internal Server Error")


@router.post("/update-calculation-methods")
@inject
async def update_report_calculations(
    data: CalculationMethodsRequest, current_user: dict = Depends(get_current_user)
):
    """
    Update the calculation methods for the report.
    """
    try:
        report = await get_report(data.chat_id, str(current_user.id))
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        updated_report = await update_calculation_methods(
            chat_id=data.chat_id, methods=data.methods
        )

        return {
            "status": "success",
            "message": "Calculation methods updated successfully",
            "report": updated_report,
        }
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Error updating calculation methods for user {current_user.id}")
        raise InternalServerError(detail="Internal Server Error")


@router.post("/update_report_step")
@inject
async def update_report_step_endpoint(
    data: UpdateReportStepRequest, current_user: dict = Depends(get_current_user)
):
    """
    Update the report step.
    """
    report = await get_report(data.chat_id, str(current_user.id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    updated_report = await update_report_step(chat_id=data.chat_id, step=data.step)

    # Convert ObjectId to string if present
    if "_id" in updated_report:
        updated_report["_id"] = str(updated_report["_id"])

    return {
        "status": "success",
        "message": "Report step updated successfully",
        "report": updated_report,
    }


@router.post("/field_analyzer", response_model=FieldAnalyzerResponse)
@inject
async def field_analyzer(
    data: FieldAnalyzerRequest, current_user: dict = Depends(get_current_user)
):
    """
    Analyze the data structure of the report.
    """
    # validate the report is exist for the chat_id
    report = await get_report(data.chat_id, str(current_user.id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # get the requirements summary
    requirements_summary = report[
        "requirements_summary"
    ]  # Need to change it in the future with the final_requirements_summary
    if not requirements_summary:
        raise HTTPException(
            status_code=400,
            detail="No requirements summary found in the report please describe phase to generate the requirements summary.",
        )

    # analyze the data structure
    try:
        response = await process_requirements_summary(
            requirements_summary, data.chat_id
        )
        return response
    except HTTPException:
        raise
    except Exception:
        logger.error("Error analyzing fields")
        raise InternalServerError(detail="Internal Server Error")


@router.post("/clarify_agent")
@inject
async def clarify_agent(
    data: ClarifyAgentRequest, current_user: dict = Depends(get_current_user)
):
    """
    Clarify the agent.
    """
    if not data.chat_id:
        raise HTTPException(status_code=400, detail="Chat ID is required")

    report = await get_report(data.chat_id, str(current_user.id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    response = await clarify_question_agent(
        query=data.query,
        userid=str(current_user.id),
        chat_id=data.chat_id,
        parent_message_id=data.parent_id,
        additional_section=data.additional_section,
    )

    if response:
        return response
    else:
        raise InternalServerError(detail="Internal Server Error")


@router.post("/regenerate-describe-chat", response_model=ChatResponse)
@inject
async def regenerate_describe_chat(
    data: RegenerateDescribeChatRequest, current_user: dict = Depends(get_current_user)
):
    """
    Regenerate the describe chat.
    """
    report = await get_report(data.chat_id, str(current_user.id))
    if not report:
        raise NotFoundError("Report not found for the user")

    # Update the requirement summary to the report
    await update_requirement_summary(
        chat_id=data.chat_id,
        summary="",
    )

    # Clear the chat messages
    await clear_chat_messages(
        chat_id=data.chat_id,
        userid=str(current_user.id),
        message_id=data.message_id,
        chat_message_collection=CHAT_MESSAGES_REPORT_COLLECTION,
        chat_history_collection=EDS_REPORT_CHAT_HISTORY_COLLECTION,
    )

    response = await report_agent.process_query(
        query=data.query,
        userid=str(current_user.id),
        chat_id=data.chat_id,
        parent_message_id=data.parent_message_id,
    )

    return ChatResponse(**response)


@router.get(
    "/describe-chat-history/{chat_id}", response_model=DescribeChatHistoryResponse
)
@inject
async def describe_chat_history(
    chat_id: int, current_user: dict = Depends(get_current_user)
):
    """
    Describe the chat history.
    """
    report = await get_report(chat_id, str(current_user.id))
    if not report:
        raise NotFoundError("Report not found for the user")

    chat_history = await get_eds_chat_history(
        chat_id,
        str(current_user.id),
        chat_history_collection=EDS_REPORT_CHAT_HISTORY_COLLECTION,
    )
    if not chat_history:
        raise NotFoundError("Chat history not found for the user")

    messages = await get_chat_messages(
        str(chat_id), chat_message_collection=CHAT_MESSAGES_REPORT_COLLECTION
    )
    if not messages:
        raise NotFoundError("No messages found in the chat history for the user")

    # Convert MongoDB documents to JSON-serializable format
    serialized_messages = []
    for message in messages:
        message_dict = dict(message).get("messages")[0]
        serialized_messages.append(message_dict)

    has_final_summary = False
    if (
        report.get("requirements_summary") is not None
        and report.get("requirements_summary") != ""
    ):
        has_final_summary = True

    return {
        "chat_id": chat_id,
        "messages": serialized_messages,
        "has_final_summary": has_final_summary,
    }


@router.get("/clarify-chat-history/{chat_id}", response_model=ClarifyAgentResponse)
@inject
async def clarify_chat_history(
    chat_id: int, current_user: dict = Depends(get_current_user)
):
    """
    Get the clarifying questions for a specific report generation chat.
    """
    report = await get_report(chat_id, str(current_user.id))
    if not report:
        raise NotFoundError("Report not found")

    clarifying_questions = report.get("clarifying_questions", [])
    additional_sections = report.get("additional_sections", [])
    if not clarifying_questions and not additional_sections:
        return ClarifyAgentResponse(
            chat_id=chat_id, clarifying_questions=[], additional_sections=[]
        )

    return ClarifyAgentResponse(
        chat_id=chat_id,
        clarifying_questions=clarifying_questions,
        additional_sections=additional_sections,
    )


@router.get("/get-report/{chat_id}")
@inject
async def get_report_endpoint(
    chat_id: int, current_user: dict = Depends(get_current_user)
):
    """
    Get the report for a specific report generation chat.

    Args:
        chat_id: The ID of the chat history to retrieve
        current_user: The current authenticated user

    Returns:
        List of chat messages with their responses
    """
    try:
        report = await get_report(chat_id, str(current_user.id))
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Convert ObjectId to string
        if "_id" in report:
            report["_id"] = str(report["_id"])

        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report : {e}")
        raise InternalServerError(detail="Internal Server Error")
