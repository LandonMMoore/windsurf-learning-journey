from typing import Callable

from sqlalchemy.orm import Session

from src.model.par_dashboard_filter_configurations import (
    ParDashboardFilterConfigurations,
)
from src.repository.base_repository import BaseRepository


class ParDashboardFilterConfigurationsRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ParDashboardFilterConfigurations)
