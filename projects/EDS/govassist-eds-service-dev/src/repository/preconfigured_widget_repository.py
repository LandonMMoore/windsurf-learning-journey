from typing import Callable

from sqlalchemy.orm import Session

from src.model.preconfigured_widget_model import PreconfiguredWidget
from src.repository.base_repository import BaseRepository


class PreconfiguredWidgetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, PreconfiguredWidget)
