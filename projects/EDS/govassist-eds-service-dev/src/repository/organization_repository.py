from typing import Callable

from sqlalchemy.orm import Session

from src.model.organization_model import Organization
from src.repository.base_repository import BaseRepository


class OrganizationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, Organization)
