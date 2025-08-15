from typing import Callable

from sqlalchemy.orm import Session

from src.repository.award_repository import AwardRepository
from src.services.base_service import BaseService


class AwardService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(AwardRepository(session_factory))
