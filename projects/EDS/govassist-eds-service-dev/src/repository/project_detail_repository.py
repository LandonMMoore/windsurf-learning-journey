from typing import Callable

from sqlalchemy.orm import Session

from src.model.project_detail_model import ProjectDetails
from src.repository.base_repository import BaseRepository


class ProjectDetailRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ProjectDetails)
