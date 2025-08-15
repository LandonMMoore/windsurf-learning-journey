from typing import Callable

from sqlalchemy.orm import Session

from src.repository.master_project_repository import MasterProjectRepository
from src.services.base_service import BaseService


class MasterProjectService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(MasterProjectRepository(session_factory))
