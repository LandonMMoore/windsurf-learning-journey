from typing import Callable

from sqlalchemy.orm import Session

from src.repository.fund_repository import FundRepository
from src.services.base_service import BaseService


class FundService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(FundRepository(session_factory))
