from typing import Callable

from sqlalchemy.orm import Session

from src.model.par_model import Par
from src.repository.base_repository import BaseRepository


class ParRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, Par)
