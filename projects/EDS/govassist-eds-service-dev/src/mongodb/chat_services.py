from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from src.core.exceptions import DuplicatedError, NotFoundError
from src.mongodb.client import get_async_database
from src.mongodb.collections import (
    CHAT_MESSAGES_COLLECTION,
    EDS_CHAT_HISTORY_COLLECTION,
    ChatMessage,
    EDSChatHistory,
    Message,
)


class ChatType(Enum):
    EDS_ASSISTANT = "EDS_ASSISTANT"
    DYNAMIC_REPORT_GENERATION = "DYNAMIC_REPORT_GENERATION"


async def get_eds_chat_history_collection(collection) -> AsyncIOMotorCollection:
    db = await get_async_database()
    return db[collection]


async def get_chat_messages_collection(collection) -> AsyncIOMotorCollection:
    """Get the chat_messages collection"""
    db = await get_async_database()
    return db[collection]


async def create_eds_chat_history(
    title: str,
    userid: Optional[str] = None,
    type: Optional[ChatType] = ChatType.EDS_ASSISTANT,
    chat_history_collection=EDS_CHAT_HISTORY_COLLECTION,
) -> Dict[str, Any]:
    """Create a new EDS chat history entry"""
    collection = await get_eds_chat_history_collection(chat_history_collection)

    # Get the next id
    last_doc = await collection.find_one(sort=[("id", -1)])
    next_id = 1 if not last_doc else last_doc["id"] + 1

    chat_history = EDSChatHistory(
        id=next_id,
        userid=userid,
        title=title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        type=type,
    )

    await collection.insert_one(chat_history.model_dump())
    return chat_history.model_dump()


async def create_chat_message(
    eds_chat_history_id: str,
    query: str,
    response: str,
    userid: str,
    parent_message_id: Optional[int] = 0,
    chat_message_collection=CHAT_MESSAGES_COLLECTION,
    chat_history_collection=EDS_CHAT_HISTORY_COLLECTION,
) -> Dict[str, Any]:

    collection = await get_chat_messages_collection(chat_message_collection)
    chat_history_collection = await get_eds_chat_history_collection(
        chat_history_collection
    )

    # Only verify chat history exists and belongs to user
    chat_history = await chat_history_collection.find_one(
        {"id": int(eds_chat_history_id), "userid": userid}
    )

    if not chat_history:
        raise NotFoundError("Chat history not found or does not belong to user")

    last_doc = await collection.find_one(sort=[("id", -1)])
    next_id = 1 if not last_doc else last_doc["id"] + 1

    last_message = await collection.find_one(
        {"eds_chat_history_id": eds_chat_history_id}, sort=[("messages.id", -1)]
    )
    next_message_id = 1
    if last_message and last_message.get("messages"):
        next_message_id = max(msg["id"] for msg in last_message["messages"]) + 1
    message = Message(
        id=next_message_id,
        query=query,
        response=response,
        created_at=datetime.utcnow(),
        parent_message_id=parent_message_id,
    )
    chat_message = ChatMessage(
        id=next_id,
        eds_chat_history_id=eds_chat_history_id,
        messages=[message],
    )
    # Update chat history's updated_at field
    await chat_history_collection.update_one(
        {"id": int(eds_chat_history_id)}, {"$set": {"updated_at": datetime.utcnow()}}
    )

    # Insert the new chat message
    result = await collection.insert_one(chat_message.model_dump())

    if not result.inserted_id:
        raise DuplicatedError(
            "I'm sorry, I'm not able to process your request. Please try again later."
        )
    return chat_message.model_dump()


async def get_eds_chat_history(
    chat_id: int, userid: str, chat_history_collection=EDS_CHAT_HISTORY_COLLECTION
) -> Optional[Dict[str, Any]]:
    """Get EDS chat history by ID and user ID"""
    collection = await get_eds_chat_history_collection(chat_history_collection)
    return await collection.find_one({"id": chat_id, "userid": userid})


async def get_chat_messages(
    eds_chat_history_id: str,
    userid: str = None,
    chat_message_collection=CHAT_MESSAGES_COLLECTION,
) -> List[Dict[str, Any]]:
    """Get all chat messages for a given EDS chat history ID"""
    collection = await get_chat_messages_collection(chat_message_collection)
    cursor = collection.find({"eds_chat_history_id": eds_chat_history_id})
    return await cursor.to_list(length=None)


async def update_eds_chat_history(
    chat_id: int,
    userid: str,
    title: Optional[str] = None,
    chat_history_collection=EDS_CHAT_HISTORY_COLLECTION,
) -> bool:
    """Update EDS chat history title"""
    collection = await get_eds_chat_history_collection(chat_history_collection)
    update_data = {"updated_at": datetime.utcnow()}
    if title:
        update_data["title"] = title

    result = await collection.update_one(
        {"id": chat_id, "userid": userid}, {"$set": update_data}
    )
    return result.modified_count > 0


async def get_all_chat_histories(
    userid: str,
    page: int = 1,
    page_size: int = 10,
    type: Optional[ChatType] = ChatType.EDS_ASSISTANT,
    chat_history_collection=EDS_CHAT_HISTORY_COLLECTION,
) -> Dict[str, Any]:
    """Get paginated chat histories with their titles in descending order (newest first)"""
    collection = await get_eds_chat_history_collection(chat_history_collection)

    # Calculate skip value for pagination
    skip = (page - 1) * page_size

    if type == ChatType.EDS_ASSISTANT:
        filter = {"type": {"$in": [None, type.value]}}
    else:
        filter = {"type": type.value}

    filter = {**filter, "userid": userid}

    # Get total count
    total = await collection.count_documents(filter)

    # Get paginated results for the user
    cursor = (
        collection.find(filter, {"id": 1, "title": 1, "updated_at": 1})
        .sort("updated_at", -1)
        .skip(skip)
        .limit(page_size)
    )

    histories = await cursor.to_list(length=None)

    # Calculate pagination info
    has_next = (skip + page_size) < total
    has_previous = page > 1

    return {
        "items": histories,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": has_next,
        "has_previous": has_previous,
    }


async def clear_chat_messages(
    chat_id: int,
    userid: str,
    message_id: int,
    chat_history_collection=EDS_CHAT_HISTORY_COLLECTION,
    chat_message_collection=CHAT_MESSAGES_COLLECTION,
) -> bool:
    """Clear chat messages for a given chat ID and user ID"""
    chat_history = await get_eds_chat_history(chat_id, userid, chat_history_collection)
    if not chat_history:
        raise NotFoundError("Chat history not found")
    collection = await get_chat_messages_collection(chat_message_collection)
    return await collection.delete_many(
        {"eds_chat_history_id": str(chat_id), "messages.id": {"$gte": message_id}}
    )
