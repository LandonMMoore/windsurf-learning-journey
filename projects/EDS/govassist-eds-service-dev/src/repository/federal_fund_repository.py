from typing import Callable

from sqlalchemy.orm import Session

from src.model.federal_fund_model import FederalFund
from src.repository.base_repository import BaseRepository


class FederalFundRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, FederalFund)
