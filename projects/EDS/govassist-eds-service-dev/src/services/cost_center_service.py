from typing import Callable

from sqlalchemy.orm import Session

from src.repository.cost_center_repository import CostCenterRepository
from src.services.base_service import BaseService


class CostCenterService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(CostCenterRepository(session_factory))
