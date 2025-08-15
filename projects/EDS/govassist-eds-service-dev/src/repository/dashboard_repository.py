from typing import Callable, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from src.core.config import configs
from src.core.exceptions import DuplicatedError, ValidationError
from src.model.dashboard_favorite_model import DashboardFavorite
from src.model.dashboard_model import Dashboard, VisibilityType
from src.model.dashboard_share_model import DashboardShare
from src.repository.base_repository import BaseRepository
from src.schema.dashboard_schema import DashboardFind, ShareType, ShareUser


class DashboardRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, Dashboard)

    def get_dashboards(self, user_id: int, find: DashboardFind):
        with self.session_factory() as session:
            created_by_me = find.created_by_me
            shared_by_me = find.shared_by_me
            my_private_dashboards = find.my_private_dashboards
            my_favorites = find.my_favorites
            search = find.search

            base_query = session.query(Dashboard.id)

            if created_by_me:
                base_query = base_query.filter(Dashboard.created_by == user_id)
            elif shared_by_me:
                base_query = base_query.filter(
                    or_(
                        # Get dashboards where user is in share list
                        Dashboard.id.in_(
                            session.query(DashboardShare.dashboard_id).filter(
                                DashboardShare.user_id == user_id
                            )
                        ),
                        # Get dashboards created by user that are shared
                        and_(
                            Dashboard.created_by == user_id,
                            Dashboard.visibility == ShareType.SHARED,
                        ),
                    )
                )

            elif my_private_dashboards:
                base_query = base_query.filter(Dashboard.created_by == user_id).filter(
                    Dashboard.visibility == VisibilityType.PRIVATE
                )

            elif my_favorites:
                base_query = base_query.filter(
                    Dashboard.id.in_(
                        session.query(DashboardFavorite.dashboard_id).filter(
                            DashboardFavorite.user_id == user_id
                        )
                    ),
                    or_(
                        Dashboard.visibility != "PRIVATE",
                        Dashboard.created_by == user_id,
                    ),
                )
            else:
                base_query = base_query.filter(
                    or_(
                        Dashboard.created_by == user_id,
                        Dashboard.visibility == VisibilityType.PUBLIC,
                        Dashboard.id.in_(
                            session.query(DashboardShare.dashboard_id).filter(
                                DashboardShare.user_id == user_id
                            )
                        ),
                    )
                )
            if search:
                base_query = base_query.filter(Dashboard.name.ilike(f"%{search}%"))

            total_count = base_query.distinct().count()

            page = find.page or configs.PAGE
            page_size = find.page_size or configs.PAGE_SIZE

            if page_size == "all":
                page_size = total_count

            query = session.query(Dashboard).filter(Dashboard.id.in_(base_query))

            ordering = find.ordering or configs.ORDERING
            ordering_list = ordering.split(",")
            query, sort_query = self._build_sort_orders(ordering_list, query)

            query = query.order_by(*sort_query)

            query = query.options(
                joinedload(Dashboard.shared_with),
                joinedload(Dashboard.favorites),
                joinedload(Dashboard.created_by_user),
            )

            page_size = int(page_size)
            results = query.limit(page_size).offset((page - 1) * page_size).all()

            return {
                "founds": results,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                    "total_count": total_count,
                    "search_term": search,
                },
            }

    def create_user_dashboard(self, schema, user_id: int):
        with self.session_factory() as session:
            data = schema.model_dump()
            data["created_by"] = user_id
            query = self.model(**data)
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
                query = self.read_by_id(query.id, eager=True)
            except IntegrityError:
                raise DuplicatedError(detail="Bad request")
            except SQLAlchemyError:
                raise ValidationError(detail="Validation error")
            return query

    def shared_dashboard(
        self,
        dashboard_id: int,
        user_id: int,
        share_type: ShareType,
        add_share_with: Optional[List[ShareUser]] = None,
        remove_share_with: Optional[List[ShareUser]] = None,
    ):

        with self.session_factory() as session:
            dashboard = (
                session.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
            )
            if not dashboard:
                raise ValidationError(
                    detail=f"Dashboard with id {dashboard_id} not found"
                )

            if dashboard.created_by != user_id:
                raise ValidationError(
                    detail="You don't have permission to share this dashboard"
                )

            dashboard.visibility = share_type

            if remove_share_with:
                for user_to_remove in remove_share_with:
                    user_id_to_remove = user_to_remove.user_id
                    if user_id_to_remove:
                        share_record = (
                            session.query(DashboardShare)
                            .filter(
                                DashboardShare.dashboard_id == dashboard_id,
                                DashboardShare.user_id == user_id_to_remove,
                            )
                            .first()
                        )
                        if share_record:
                            session.delete(share_record)

            if add_share_with and share_type == ShareType.SHARED:
                for user_to_add in add_share_with:
                    user_id_to_add = user_to_add.user_id
                    email = user_to_add.email

                    if user_id_to_add:
                        existing_share = (
                            session.query(DashboardShare)
                            .filter(
                                DashboardShare.dashboard_id == dashboard_id,
                                DashboardShare.user_id == user_id_to_add,
                            )
                            .first()
                        )

                        if not existing_share:
                            new_share = DashboardShare(
                                dashboard_id=dashboard_id,
                                user_id=user_id_to_add,
                                email=email,
                            )
                            session.add(new_share)

            try:
                session.commit()
                session.refresh(dashboard)
                return self.read_by_id(dashboard_id, eager=True)
            except IntegrityError:
                session.rollback()
                raise DuplicatedError(detail="Bad request")
            except SQLAlchemyError:
                session.rollback()
                raise ValidationError(detail="Validation error")

    def get_dashboard_share_list(self, dashboard_id: int):
        with self.session_factory() as session:
            # Get all share records for the specific dashboard
            share_records = (
                session.query(DashboardShare)
                .filter(DashboardShare.dashboard_id == dashboard_id)
                .all()
            )

            # Convert share records to ShareUser format
            share_list = [
                ShareUser(user_id=share.user_id, email=share.email)
                for share in share_records
            ]

            return share_list
