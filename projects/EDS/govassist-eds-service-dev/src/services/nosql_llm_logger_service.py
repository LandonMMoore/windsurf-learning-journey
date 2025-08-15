from src.repository.nosql_llm_logger_repository import NosqlLLMLoggerRepository


class NosqlLLMLoggerService:
    def __init__(
        self,
        nosql_llm_logger_repository: NosqlLLMLoggerRepository,
    ):
        self.nosql_llm_logger_repository = nosql_llm_logger_repository

    def get_logger_callback(
        self, metadata: dict, provider: str = "unknown", model_name: str = "unknown"
    ):

        return self.nosql_llm_logger_repository.get_logger_callback(
            metadata, provider, model_name
        )
