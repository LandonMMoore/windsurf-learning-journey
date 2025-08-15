from typing import Callable

from sqlalchemy.orm import Session

from src.repository.integration_sql_repository import IntegrationSqlRepository
from src.services.base_service import BaseService


class IntegrationSqlService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(IntegrationSqlRepository(session_factory))
