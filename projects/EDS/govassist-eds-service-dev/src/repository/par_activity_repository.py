from typing import Callable

from sqlalchemy.orm import Session

from src.model.par_activity_model import ParActivity
from src.repository.base_repository import BaseRepository


class ParActivityRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ParActivity)
