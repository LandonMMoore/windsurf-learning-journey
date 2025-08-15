from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from src.core.config import configs
from src.core.exceptions import InternalServerError

# Global client instances
_mongo_client = None
_motor_client = None


def get_mongo_client() -> MongoClient:
    """Get or create a synchronous MongoDB client instance."""
    global _mongo_client

    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(configs.MONGODB_URL)  # Test connection
            _mongo_client.admin.command("ping")
            logger.info("✅ Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise InternalServerError(detail="Internal Server Error")

    return _mongo_client


async def get_motor_client() -> AsyncIOMotorClient:
    """Get or create an asynchronous MongoDB client instance."""
    global _motor_client

    if _motor_client is None:
        try:
            _motor_client = AsyncIOMotorClient(configs.MONGODB_URL)
            # Test connection
            await _motor_client.admin.command("ping")
            logger.info("✅ Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise InternalServerError(detail="Internal Server Error")

    return _motor_client


def get_database():
    """Get the MongoDB database instance."""
    client = get_mongo_client()
    return client[configs.MONGODB_DATABASE]


async def get_async_database():
    """Get the MongoDB database instance asynchronously."""
    client = await get_motor_client()
    return client[configs.MONGODB_DATABASE]


def get_chat_collection():
    """Get the chat history collection."""
    db = get_database()
    return db[configs.MONGODB_CHAT_COLLECTION]


async def get_async_chat_collection():
    """Get the chat history collection asynchronously."""
    db = await get_async_database()
    return db[configs.MONGODB_CHAT_COLLECTION]
