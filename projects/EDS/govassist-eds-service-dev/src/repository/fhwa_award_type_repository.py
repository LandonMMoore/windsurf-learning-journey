from typing import Callable

from sqlalchemy.orm import Session

from src.model.fhwa_award_type_model import FhwaAwardType
from src.repository.base_repository import BaseRepository


class FhwaAwardTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, FhwaAwardType)
