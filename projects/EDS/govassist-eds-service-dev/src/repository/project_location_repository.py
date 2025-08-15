from typing import Callable

from sqlalchemy.orm import Session

from src.model.project_location import ProjectLocation
from src.repository.base_repository import BaseRepository


class ProjectLocationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ProjectLocation)
