import json
from typing import List

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from src.agents.rag_query_v3.unstructured_agent import query_process as query_process_v3
from src.core.dependencies import get_current_user
from src.core.exceptions import (
    DuplicatedError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)
from src.mongodb.chat_services import (
    create_chat_message,
    create_eds_chat_history,
    get_all_chat_histories,
    get_chat_messages,
    get_eds_chat_history,
)
from src.mongodb.collections import EDSAssistanceLog, EDSAssistanceStatus
from src.mongodb.eds_assistance_log import EdsAssistanceLogService
from src.schema.ai_assistent_schema import (
    ChatMessagesResponse,
    ChatRequest,
    ChatResponse,
    PaginatedChatHistoryResponse,
    ValidateQuery,
)
from src.util.es_agent import generate_title_from_query, process_nl_query
from src.util.response_sanitizer import ResponseSanitizer

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])

# Create an instance of ResponseSanitizer
response_sanitizer = ResponseSanitizer()


@router.post("", response_model=ChatResponse)
@inject
async def ai_assistant(
    data: ChatRequest, current_user: dict = Depends(get_current_user)
):

    if not data.chat_id:
        title = generate_title_from_query(data.query)
        chat_history = await create_eds_chat_history(
            title=title, userid=str(current_user.id)
        )
        data.chat_id = chat_history["id"]
        data.parent_id = 0

    # Verify chat history belongs to user
    chat_history = await get_eds_chat_history(data.chat_id, str(current_user.id))
    if not chat_history:
        raise NotFoundError("Chat history not found")

    response = await process_nl_query(
        query=data.query,
        chat_id=data.chat_id,
        parent_message_id=data.parent_id,
        userid=str(current_user.id),
    )

    # Create chat message
    await create_chat_message(
        eds_chat_history_id=str(data.chat_id),
        query=data.query,
        response=response,
        userid=str(current_user.id),
        parent_message_id=data.parent_id,
    )

    messages = await get_chat_messages(str(data.chat_id), str(current_user.id))
    if not messages:
        raise DuplicatedError(
            "I'm sorry, I'm not able to process your request. Please try again later."
        )

    last_message = messages[-1]["messages"][-1]
    message_id = last_message["id"]

    return ChatResponse(
        response=response,
        chat_id=data.chat_id,
        message_id=message_id,
        parent_message_id=data.parent_id,
    )


@router.post("/v3", response_model=ChatResponse)
@inject
async def ai_assistant_v3(
    data: ChatRequest, current_user: dict = Depends(get_current_user)
):
    try:
        ValidateQuery(**data.dict(), user_id=current_user.id)
    except ValueError as e:
        # Log validation error to MongoDB
        try:
            await EdsAssistanceLogService().create_eds_assistance_log(
                EDSAssistanceLog(
                    user_query=data.query,
                    error_message=str(e),
                    user_id=str(current_user.id),
                    chat_id=data.chat_id,
                    parent_message_id=data.parent_id,
                    status=EDSAssistanceStatus.MALICIOUS,
                )
            )
            logger.info("Malicious AI assistant query detected and logged to MongoDB")
        except Exception as logging_error:
            logger.warning(f"Failed to log malicious query to MongoDB: {logging_error}")

        # Always raise ValidationError for malicious queries
        raise ValidationError("Malicious AI assistant query detected")

    if not data.chat_id:
        title = generate_title_from_query(data.query)
        chat_history = await create_eds_chat_history(
            title=title, userid=str(current_user.id)
        )
        data.chat_id = chat_history["id"]
        data.parent_id = 0

    # Verify chat history belongs to user
    chat_history = await get_eds_chat_history(data.chat_id, str(current_user.id))
    if not chat_history:
        raise NotFoundError("Chat history not found")

    messages = await get_chat_messages(str(data.chat_id), str(current_user.id))

    last_5_messages = None
    if messages:
        messages_to_process = messages[-5:] if len(messages) >= 5 else messages
        last_5_messages = [
            {
                "query": msg["messages"][0]["query"],
                "response": msg["messages"][0]["response"],
            }
            for msg in messages_to_process
        ]

    async def response_streamer():
        response = ""
        is_sanitize = False
        try:
            async for chunk in query_process_v3(
                query=data.query,
                chat_id=data.chat_id,
                parent_message_id=data.parent_id,
                userid=str(current_user.id),
                chat_history=last_5_messages,
            ):
                if isinstance(chunk, str):
                    sanitized_chunk = response_sanitizer.sanitize_response(chunk)
                    response += sanitized_chunk
                    yield sanitized_chunk
                    if not is_sanitize and chunk != sanitized_chunk:
                        is_sanitize = True
                        try:
                            await EdsAssistanceLogService().create_eds_assistance_log(
                                EDSAssistanceLog(
                                    user_query=data.query,
                                    error_message="Response sanitized",
                                    user_id=str(current_user.id),
                                    chat_id=data.chat_id,
                                    parent_message_id=data.parent_id,
                                    status=EDSAssistanceStatus.RESPONSE_SANITIZATION_SUCCESS,
                                )
                            )
                            logger.info("Response sanitization success and logged")
                        except Exception as e:
                            logger.error(f"Error logging response sanitization: {e}")

            chat_message = await create_chat_message(
                eds_chat_history_id=str(data.chat_id),
                query=data.query,
                response=response,
                userid=str(current_user.id),
                parent_message_id=data.parent_id,
            )
            yield f"\n<END>{json.dumps({
                'chat_id': data.chat_id,
                'message_id': chat_message['messages'][0]['id'],
                'parent_message_id': data.parent_id
            })}"
        except Exception as e:
            logger.error(f"Error in EDS Assistant V3: {e}")
            yield "\n Sorry, I'm not able to process your request. Please try again later."

    return StreamingResponse(response_streamer(), media_type="text/plain")


@router.get("/chat-history", response_model=PaginatedChatHistoryResponse)
@inject
async def get_all_chat_history(
    page: int = 1, page_size: int = 10, current_user: dict = Depends(get_current_user)
):
    if page < 1:
        raise ValidationError("Page number must be greater than 0")
    if page_size < 1 or page_size > 100:
        raise ValidationError("Page size must be between 1 and 100")

    return await get_all_chat_histories(
        userid=str(current_user.id), page=page, page_size=page_size
    )


@router.get("/chat-messages/{chat_id}", response_model=List[ChatMessagesResponse])
@inject
async def get_chat_messages_by_id(
    chat_id: int, current_user: dict = Depends(get_current_user)
):
    """Get all messages for a specific chat history ID for the current user"""
    try:
        # Verify chat history exists and belongs to user
        chat_history = await get_eds_chat_history(chat_id, str(current_user.id))
        if not chat_history:
            raise NotFoundError("Chat history not found")

        messages = await get_chat_messages(str(chat_id), str(current_user.id))
        messages.sort(key=lambda x: x["messages"][0]["id"])
        return messages
    except HTTPException:
        raise
    except Exception:
        raise InternalServerError(detail="Internal Server Error")
