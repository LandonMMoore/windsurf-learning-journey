from typing import Callable

from sqlalchemy.orm import Session

from src.model.fhwa_model import Fhwa
from src.repository.base_repository import BaseRepository


class FhwaRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, Fhwa)
