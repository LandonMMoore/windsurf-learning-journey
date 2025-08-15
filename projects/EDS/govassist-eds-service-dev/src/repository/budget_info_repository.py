from typing import Callable

from sqlalchemy.orm import Session

from src.model.budget_info_model import BudgetInfo
from src.repository.base_repository import BaseRepository


class BudgetInfoRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, BudgetInfo)
