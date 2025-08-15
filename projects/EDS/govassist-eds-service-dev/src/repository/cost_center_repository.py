from typing import Callable

from sqlalchemy.orm import Session

from src.model.cost_center_model import CostCenter
from src.repository.base_repository import BaseRepository


class CostCenterRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, CostCenter)
