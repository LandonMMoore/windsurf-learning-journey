from typing import Callable, Optional

from sqlalchemy.orm import Session

from src.model.widget_favorite_model import WidgetFavorite
from src.repository.base_repository import BaseRepository
from src.schema.base_schema import FindBase


class WidgetFavoriteRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, WidgetFavorite)

    def get_favorite(self, user_id: int, widget_id: int) -> Optional[WidgetFavorite]:
        """Get a favorite by user_id and widget_id."""
        with self.session_factory() as session:
            return (
                session.query(WidgetFavorite)
                .filter(
                    WidgetFavorite.user_id == user_id,
                    WidgetFavorite.widget_id == widget_id,
                )
                .first()
            )

    def toggle_favorite(self, user_id: int, widget_id: int) -> bool:
        """
        Toggle favorite status for a widget.
        Returns True if widget is now favorited, False if it was removed.
        """
        with self.session_factory() as session:
            favorite = self.get_favorite(user_id, widget_id)
            if favorite:
                session.delete(favorite)
                session.commit()
                return False
            else:
                new_favorite = WidgetFavorite(user_id=user_id, widget_id=widget_id)
                session.add(new_favorite)
                session.commit()
                return True

    def get_user_favorites(self, user_id: int, find: FindBase) -> dict:
        """
        Get all favorited widgets for a user with pagination.

        Args:
            user_id: The ID of the user
            find: The find options for pagination and sorting

        Returns:
            Dictionary containing the list of favorited widgets and search options
        """
        find.user_id = user_id
        return self.read_by_options(find, eager=True)

    def get_favorite_widget_ids(self, user_id: int) -> set:
        with self.session_factory() as session:
            return set(
                session.query(WidgetFavorite.widget_id)
                .filter(WidgetFavorite.user_id == user_id)
                .all()
            )
