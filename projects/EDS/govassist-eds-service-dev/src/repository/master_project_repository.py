from typing import Callable

from sqlalchemy.orm import Session

from src.model.master_project_model import MasterProject
from src.repository.base_repository import BaseRepository


class MasterProjectRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, MasterProject)
