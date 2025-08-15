from abs_langchain_suite.logging.token_usage import DBTokenUsageLogger
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.config import configs


class NosqlLLMLoggerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection_name = "llm_token_usage"
        self.db = db

    def get_logger_callback(
        self, metadata: dict, provider: str = "unknown", model_name: str = "unknown"
    ):
        metadata["module"] = configs.PROJECT_NAME
        metadata["environment"] = configs.ENV

        return DBTokenUsageLogger(
            self.db,
            self.collection_name,
            metadata=metadata,
            provider=provider,
            model_name=model_name,
        )
