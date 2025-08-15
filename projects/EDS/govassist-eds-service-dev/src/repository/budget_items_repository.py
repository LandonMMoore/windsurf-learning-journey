from typing import Callable

from sqlalchemy.orm import Session

from src.model.budget_items_model import BudgetItems
from src.repository.base_repository import BaseRepository


class BudgetItemsRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, BudgetItems)
