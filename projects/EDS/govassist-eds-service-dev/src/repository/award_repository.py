from typing import Callable

from sqlalchemy.orm import Session

from src.model.award_model import Award
from src.repository.base_repository import BaseRepository


class AwardRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, Award)
