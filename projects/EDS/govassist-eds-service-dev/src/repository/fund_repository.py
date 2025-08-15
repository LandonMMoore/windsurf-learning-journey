from typing import Callable

from sqlalchemy.orm import Session

from src.model.fund_model import Fund
from src.repository.base_repository import BaseRepository


class FundRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, Fund)
