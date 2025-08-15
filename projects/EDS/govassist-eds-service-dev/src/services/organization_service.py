from typing import Callable

from sqlalchemy.orm import Session

from src.repository.organization_repository import OrganizationRepository
from src.services.base_service import BaseService


class OrganizationService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(OrganizationRepository(session_factory))
