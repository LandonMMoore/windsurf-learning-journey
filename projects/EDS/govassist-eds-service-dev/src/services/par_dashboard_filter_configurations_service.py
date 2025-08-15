from typing import Callable

from sqlalchemy.orm import Session

from src.repository.par_dashboard_filter_configurations_repository import (
    ParDashboardFilterConfigurationsRepository,
)
from src.services.base_service import BaseService


class ParDashboardFilterConfigurationsService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(ParDashboardFilterConfigurationsRepository(session_factory))
        self._session_factory = session_factory
