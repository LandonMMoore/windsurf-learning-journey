from typing import Callable, Optional

from sqlalchemy.orm import Session

from src.model.dashboard_favorite_model import DashboardFavorite
from src.repository.base_repository import BaseRepository
from src.schema.base_schema import FindBase


class DashboardFavoriteRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, DashboardFavorite)

    def get_favorite(
        self, user_id: int, dashboard_id: int
    ) -> Optional[DashboardFavorite]:
        with self.session_factory() as session:
            return (
                session.query(DashboardFavorite)
                .filter(
                    DashboardFavorite.user_id == user_id,
                    DashboardFavorite.dashboard_id == dashboard_id,
                )
                .first()
            )

    def toggle_favorite(self, user_id: int, dashboard_id: int) -> bool:
        with self.session_factory() as session:
            favorite = self.get_favorite(user_id, dashboard_id)
            if favorite:
                session.delete(favorite)
                session.commit()
                return False
            else:
                new_favorite = DashboardFavorite(
                    user_id=user_id, dashboard_id=dashboard_id
                )
                session.add(new_favorite)
                session.commit()
                return True

    def get_user_favorites(self, user_id: int, find: FindBase) -> dict:
        """
        Get all favorited dashboards for a user with pagination.
        """
        find.user_id = user_id
        return self.read_by_options(find, eager=True)

    def get_favorite_dashboard_ids(self, user_id: int, find: FindBase) -> set:
        """
        Get all favorite dashboard IDs for a user.
        """
        find.user_id = user_id
        return self.read_by_options(find, eager=True)
