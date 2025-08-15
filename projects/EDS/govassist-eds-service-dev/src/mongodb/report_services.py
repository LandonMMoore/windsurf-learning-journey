from datetime import datetime
from typing import Dict, List, Optional, Union

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from src.core.config import configs
from src.mongodb.collections import (
    REPORT_COLLECTION,
    Message,
    ReportGeneration,
    ReportGenerationStep,
)

# Initialize MongoDB client
client = AsyncIOMotorClient(configs.MONGODB_URL)
db = client[configs.MONGODB_DATABASE]
report_collection = db[REPORT_COLLECTION]


async def create_report(
    chat_id: int, userid: str, final_requirements_summary: str, report_type: str
) -> Dict:
    """Create a new report generation document"""
    report = ReportGeneration(
        chat_id=chat_id,
        userid=userid,
        final_requirements_summary=final_requirements_summary,
        report_type=report_type,
    )

    document = report.dict()
    result = await report_collection.insert_one(document)

    if result.inserted_id:
        return await get_report(chat_id, userid)
    raise Exception("Failed to create report document")


async def get_report(chat_id: int, userid: str) -> Optional[Dict]:
    """Retrieve report document by chat ID"""
    report = await report_collection.find_one({"chat_id": chat_id, "userid": userid})
    return report


async def update_report_step(
    chat_id: int, step: ReportGenerationStep, additional_data: Optional[Dict] = None
) -> Optional[Dict]:
    """Update report step and any additional data"""
    update_dict = {"current_step": step, "updated_at": datetime.utcnow()}

    if additional_data:
        update_dict.update(additional_data)

    if step == ReportGenerationStep.REPORT_GENERATION_COMPLETED:
        update_dict["completed_at"] = datetime.utcnow()

    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {"$set": update_dict},
        return_document=ReturnDocument.AFTER,
    )
    return result


async def add_clarifying_question(
    chat_id: int, userid: str, query: str, response: str, parent_message_id: int
) -> Optional[Dict]:
    """Add a clarifying question to the report"""
    report = await get_report(chat_id, userid)
    clarifying_questions = report.get("clarifying_questions")
    next_message_id = 1
    if clarifying_questions:
        next_message_id = max(msg["id"] for msg in clarifying_questions) + 1

    message = Message(
        id=next_message_id,
        query=query,
        response=response,
        created_at=datetime.utcnow(),
        parent_message_id=parent_message_id,
    )

    # Convert Message object to dictionary
    message_dict = message.model_dump()

    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {
            "$push": {"clarifying_questions": message_dict},
            "$set": {
                "updated_at": datetime.utcnow(),
                "current_step": ReportGenerationStep.CLARIFYING_QUESTIONS,
            },
        },
        return_document=ReturnDocument.AFTER,
    )
    return result


async def add_additional_section_question(
    chat_id: int, userid: str, query: str, response: str, parent_message_id: int
) -> Optional[Dict]:
    """Add an additional section question to the report"""
    report = await get_report(chat_id, userid)
    additional_sections = report.get("additional_sections")
    next_message_id = 1
    if additional_sections:
        next_message_id = max(msg["id"] for msg in additional_sections) + 1

    message = Message(
        id=next_message_id,
        query=query,
        response=response,
        created_at=datetime.utcnow(),
        parent_message_id=parent_message_id,
    )

    # Convert Message object to dictionary
    message_dict = message.model_dump()

    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {
            "$push": {"additional_sections": message_dict},
            "$set": {
                "updated_at": datetime.utcnow(),
            },
        },
        return_document=ReturnDocument.AFTER,
    )
    return result


async def update_question_response(
    chat_id: int, question_index: int, response: Union[str, Dict], userid: str
) -> Optional[Dict]:
    """Update a clarifying question with user's response"""
    # First, get the current questions array
    report = await get_report(chat_id, userid)
    if not report or "clarifying_questions" not in report:
        raise ValueError("Report not found or no questions exist")

    questions = report["clarifying_questions"]
    if question_index >= len(questions):
        raise ValueError("Question index out of range")

    # Update the specific question with the response
    questions[question_index]["response"] = response
    questions[question_index]["answered"] = True
    questions[question_index]["response_timestamp"] = datetime.utcnow()

    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {"$set": {"clarifying_questions": questions, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return result


async def update_selected_fields(chat_id: int, fields: List[Dict]) -> Optional[Dict]:
    """Update the selected fields for the report"""
    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {"$set": {"selected_fields": fields, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return result


async def update_calculation_methods(
    chat_id: int, methods: List[Dict]
) -> Optional[Dict]:
    """Update the calculation methods for the report"""
    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {"$set": {"calculation_methods": methods, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return result


async def set_report_generation_failed(
    chat_id: int, error_message: str
) -> Optional[Dict]:
    """Mark report generation as failed with error message"""
    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {
            "$set": {
                "current_step": ReportGenerationStep.REPORT_GENERATION_FAILED,
                "error_message": error_message,
                "updated_at": datetime.utcnow(),
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    return result


async def get_user_reports(userid: str) -> List[Dict]:
    """Get all reports for a specific user"""
    cursor = report_collection.find({"userid": userid})
    reports = await cursor.to_list(length=None)
    return reports


async def get_reports_by_step(step: ReportGenerationStep) -> List[Dict]:
    """Get all reports in a specific step"""
    cursor = report_collection.find({"current_step": step})
    reports = await cursor.to_list(length=None)
    return reports


async def update_time_period(chat_id: int, time_period: Dict) -> Optional[Dict]:
    """Update the time period for the report"""
    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {"$set": {"time_period": time_period, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return result


async def update_data_sources(chat_id: int, data_sources: List[str]) -> Optional[Dict]:
    """Update the data sources for the report"""
    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {"$set": {"data_sources": data_sources, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return result


async def update_requirement_summary(chat_id: int, summary: str) -> Optional[Dict]:
    """Update the requirement summary for the report"""
    result = await report_collection.find_one_and_update(
        {"chat_id": chat_id},
        {
            "$set": {
                "final_requirements_summary": summary,
                "requirements_summary": summary,
                "updated_at": datetime.utcnow(),
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    return result
