from typing import Callable

from sqlalchemy.orm import Session

from src.repository.fhwa_award_type_repository import FhwaAwardTypeRepository
from src.services.base_service import BaseService


class FhwaAwardTypeService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(FhwaAwardTypeRepository(session_factory))
