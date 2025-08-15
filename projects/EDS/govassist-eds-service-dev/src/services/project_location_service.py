from typing import Callable

from sqlalchemy.orm import Session

from src.repository.project_location_repository import ProjectLocationRepository
from src.services.base_service import BaseService


class ProjectLocationService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(ProjectLocationRepository(session_factory))
