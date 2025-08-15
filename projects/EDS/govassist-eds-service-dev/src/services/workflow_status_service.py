from typing import Callable

from sqlalchemy.orm import Session

from src.repository.workflow_status_repository import WorkflowStatusRepository
from src.services.base_service import BaseService


class WorkflowStatusService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(WorkflowStatusRepository(session_factory))
