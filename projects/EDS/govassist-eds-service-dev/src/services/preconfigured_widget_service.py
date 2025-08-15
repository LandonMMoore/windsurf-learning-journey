from typing import Callable

from sqlalchemy.orm import Session

from src.repository.preconfigured_widget_repository import PreconfiguredWidgetRepository
from src.services.base_service import BaseService


class PreconfiguredWidgetService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(PreconfiguredWidgetRepository(session_factory))
