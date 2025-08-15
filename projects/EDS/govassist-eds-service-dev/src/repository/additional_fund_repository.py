from typing import Callable

from sqlalchemy.orm import Session

from src.model.additional_fund_model import AdditionalFund
from src.repository.base_repository import BaseRepository


class AdditionalFundRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, AdditionalFund)
