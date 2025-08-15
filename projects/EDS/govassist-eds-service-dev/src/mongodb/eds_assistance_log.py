import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection

from src.core.config import configs
from src.mongodb.client import get_async_database
from src.mongodb.collections import (
    EDS_ASSISTANCE_LOG_COLLECTION,
    EDSAssistanceLog,
    EDSAssistanceStatus,
)


class EdsAssistanceLogService:
    """Service for managing EDS interactions in MongoDB"""

    def __init__(self):
        self.enabled = configs.ENABLE_EDS_ASSISTANCE_LOGGING or False

    async def get_eds_assistance_log_collection(self) -> AsyncIOMotorCollection:
        """Get the eds_assistance_log collection"""
        db = await get_async_database()
        return db[EDS_ASSISTANCE_LOG_COLLECTION]

    async def create_eds_assistance_log(
        self,
        log: EDSAssistanceLog,
    ) -> Dict[str, Any]:
        """Create a new eds assistance log record with initial data"""
        if not self.enabled:
            return {}

        try:
            collection = await self.get_eds_assistance_log_collection()

            await collection.insert_one(log.model_dump())
            print(log.model_dump(), "log")
            return log.model_dump()

        except Exception as e:
            logger.error(
                f"Failed to create eds assistance log record: {str(e)}", exc_info=True
            )
            # Don't raise exception to avoid breaking the main flow
            return {}

    async def update_eds_assistance_log(
        self,
        interaction_id: int,
        updates: Dict[str, Any],
        retry_count: int = 0,
    ) -> bool:
        """Update an existing interaction record with retry logic"""
        if not self.enabled:
            return True

        try:
            collection = await self.get_interactions_collection()

            # Add updated timestamp
            updates["timestamp"] = datetime.utcnow()

            result = await collection.update_one(
                {"id": interaction_id}, {"$set": updates}
            )

            if result.modified_count > 0:
                logger.debug(f"Updated interaction record with ID: {interaction_id}")
                return True
            else:
                logger.warning(f"No interaction record found with ID: {interaction_id}")
                return False

        except Exception as e:
            logger.error(
                f"Failed to update interaction record {interaction_id}: {str(e)}"
            )

            # Retry logic
            if retry_count < self.max_retries:
                await asyncio.sleep(self.retry_delay * (2**retry_count))
                return await self.update_interaction(
                    interaction_id, updates, retry_count + 1
                )

            # Don't raise exception to avoid breaking the main flow
            return False

    async def log_interaction_success(
        self,
        interaction_id: int,
        generated_es_query: Optional[Dict] = None,
        response_summary: Optional[str] = None,
        processing_latency_ms: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Log successful interaction completion"""
        updates = {
            "status": EDSAssistanceStatus.SUCCESS,
            "generated_es_query": generated_es_query,
            "response_summary": response_summary,
            "processing_latency_ms": processing_latency_ms,
        }

        if metadata:
            updates["metadata"] = metadata

        return await self.update_interaction(interaction_id, updates)

    async def log_interaction_error(
        self,
        interaction_id: int,
        error_message: str,
        processing_latency_ms: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Log interaction error"""
        updates = {
            "status": EDSAssistanceStatus.FAILED,
            "error_message": error_message,
            "processing_latency_ms": processing_latency_ms,
        }

        if metadata:
            updates["metadata"] = metadata

        return await self.update_interaction(interaction_id, updates)

    async def log_interaction_incomplete(
        self,
        interaction_id: int,
        reason: str,
        processing_latency_ms: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Log incomplete interaction"""
        updates = {
            "status": EDSAssistanceStatus.FAILED,
            "error_message": reason,
            "processing_latency_ms": processing_latency_ms,
        }

        if metadata:
            updates["metadata"] = metadata

        return await self.update_interaction(interaction_id, updates)


eds_assistance_log_service = EdsAssistanceLogService()
