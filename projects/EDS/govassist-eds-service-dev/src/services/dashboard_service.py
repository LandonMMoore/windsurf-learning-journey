from typing import Any, Callable, Dict, List, Optional

from loguru import logger
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.core.exceptions import (
    FailedToCreateError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
)
from src.elasticsearch.constants import get_filter_configuration_for_index
from src.model.dashboard_model import VisibilityType
from src.repository.dashboard_repository import DashboardRepository
from src.repository.dashboard_widget_repository import DashboardWidgetRepository
from src.schema.dashboard_favorite_schema import DashboardFavoriteFind
from src.schema.dashboard_schema import (
    DashboardCreate,
    DashboardFind,
    RecentDashboardsResponse,
    ShareType,
    ShareUser,
)
from src.services.base_service import BaseService
from src.services.dashboard_favorite_service import DashboardFavoriteService
from src.services.index_compatibility_service import IndexCompatibilityService


class DashboardService(BaseService):
    def __init__(
        self,
        session_factory: Callable[..., Session],
        dashboard_favorite_service: DashboardFavoriteService,
        index_compatibility_service: IndexCompatibilityService,
    ):
        super().__init__(DashboardRepository(session_factory))
        self.dashboard_favorite_service = dashboard_favorite_service
        self.index_compatibility_service = index_compatibility_service

    def get_dashboards(self, user_id: int, find: DashboardFind):
        return self._repository.get_dashboards(user_id, find)

    def get_list(self, find: DashboardFind, user_id: int):

        if find.created_by_me and user_id:
            find.created_by = user_id

        result = super().get_list(find)

        if user_id and result.get("founds"):
            for dashboard in result["founds"]:
                dashboard.is_my_dashboard = dashboard.created_by == user_id

        return result

    def add(self, dashboard: DashboardCreate, user_id: int):
        return self._repository.create_user_dashboard(dashboard, user_id)

    def get_recent_dashboards(self, user_id: int) -> RecentDashboardsResponse:
        """
        Get recent dashboards based on creation date, favorites, and created by.

        Args:
            user_id: The ID of the user to get recent dashboards for

        Returns:
            RecentDashboardsResponse containing three lists of recent dashboards
        """
        # Get recent created dashboards (excluding private ones)
        recent_created = []
        recent_created_by = []
        favorite_dashboards = []

        with self._repository.session_factory() as session:
            try:
                recent_created = (
                    session.query(self._repository.model)
                    .filter(
                        or_(
                            self._repository.model.created_by == user_id,
                            (
                                self._repository.model.visibility
                                != VisibilityType.PRIVATE
                            ),
                        )
                    )
                    .order_by(self._repository.model.created_at.desc())
                    .limit(3)
                    .all()
                )
            except Exception as e:
                logger.error(
                    "error occured while fetching recent created dashboards", e
                )
            # Set is_my_dashboard flag
            # TODO: May be need in the future
            # for dashboard in recent_created:
            #     dashboard.is_my_dashboard = dashboard.created_by == user_id

        # Get recent favorites
        recent_favorites_find = DashboardFavoriteFind(
            ordering="-created_at",
            page=1,
            page_size=3,
        )

        favorite_result = self.dashboard_favorite_service.get_user_favorites(
            user_id, recent_favorites_find
        )
        for favorite in favorite_result.get("founds"):
            favorite_dashboards.append(favorite.dashboard)

        # TODO: May be need in the future
        # favorite_dashboards = []
        # if favorite_result.get("founds"):
        #     for favorite in favorite_result["founds"]:
        #         if hasattr(favorite, "dashboard"):
        #             dashboard = favorite.dashboard
        #             # dashboard.is_my_dashboard = dashboard.created_by == user_id

        #             if not (
        #                 dashboard.visibility == VisibilityType.PRIVATE
        #                 and dashboard.created_by != user_id
        #             ):
        #                 favorite_dashboards.append(dashboard)

        recent_created_by = (
            session.query(self._repository.model)
            .filter(
                or_(
                    self._repository.model.created_by == user_id,
                )
            )
            .order_by(self._repository.model.created_at.desc())
            .limit(3)
            .all()
        )
        return RecentDashboardsResponse(
            recent_created=recent_created,
            recent_favorites=favorite_dashboards,
            recent_created_by=recent_created_by,
        )

    def clone_dashboard(self, dashboard_id: int, user_id: int):
        """Clone a dashboard and all its widgets"""
        with self._repository.session_factory() as session:
            try:
                source_dashboard = (
                    session.query(self._repository.model)
                    .filter_by(id=dashboard_id)
                    .first()
                )
                if not source_dashboard:
                    raise ValueError(f"Dashboard with ID {dashboard_id} not found")

                dashboard_dict = {
                    key: value
                    for key, value in source_dashboard.__dict__.items()
                    if not key.startswith("_")
                    and key
                    not in [
                        "id",
                        "uuid",
                        "created_at",
                        "updated_at",
                        "dashboard_widgets",
                        "favorites",  # Explicitly exclude favorites
                    ]
                }

                dashboard_dict["name"] = f"{dashboard_dict['name']} (Copy)"

                new_dashboard = self._repository.model(**dashboard_dict)
                new_dashboard.created_by = user_id
                session.add(new_dashboard)
                session.flush()
                session.refresh(new_dashboard)
                source_widgets = source_dashboard.dashboard_widgets

                if source_widgets:
                    widget_repo = DashboardWidgetRepository(
                        self._repository.session_factory
                    )

                    for source_widget in source_widgets:
                        widget_dict = {
                            key: value
                            for key, value in source_widget.__dict__.items()
                            if not key.startswith("_")
                            and key
                            not in [
                                "id",
                                "uuid",
                                "created_at",
                                "updated_at",
                                "favorites",
                            ]  # Explicitly exclude favorites
                        }

                        new_widget = widget_repo.model(**widget_dict)
                        new_widget.dashboard_id = new_dashboard.id
                        session.add(new_widget)

                session.commit()
                return self._repository.read_by_id(new_dashboard.id, eager=True)

            except Exception:
                session.rollback()
                raise InternalServerError(detail="Internal Server Error")

    def shared_dashboard(
        self,
        dashboard_id: int,
        user_id: int,
        share_type: ShareType,
        add_share_with: Optional[List[ShareUser]] = None,
        remove_share_with: Optional[List[ShareUser]] = None,
    ):
        return self._repository.shared_dashboard(
            dashboard_id, user_id, share_type, add_share_with, remove_share_with
        )

    def get_dashboard(self, dashboard_id: int, user_id: int) -> bool:
        dashboard = self.get_by_id(dashboard_id)

        # User created the dashboard
        if dashboard.created_by == user_id:
            return dashboard

        # Dashboard is PUBLIC
        if dashboard.visibility == "PUBLIC":
            return dashboard

        # Dashboard is SHARED with user
        if dashboard.visibility == "SHARED":
            for share in dashboard.shared_with:
                if share.user_id == user_id:
                    return dashboard

        raise UnauthorizedError(
            detail="You don't have permission to access this dashboard"
        )

    def get_dashboard_share_list(self, dashboard_id: int, user_id: int):
        # First verify the dashboard exists
        dashboard = self.get_by_id(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard with ID {dashboard_id} not found")

        if not dashboard.created_by == user_id:
            raise UnauthorizedError(
                detail="You don't have permission to access this dashboard"
            )

        shared_list = self._repository.get_dashboard_share_list(dashboard_id)
        return {"visibility": dashboard.visibility, "shared_with": shared_list}

    def bulk_dashboard_delete(self, ids: List[int], user_id: int):
        with self._repository.session_factory() as session:
            try:
                # First verify all dashboards exist and user has permission
                dashboards = (
                    session.query(self._repository.model)
                    .filter(
                        self._repository.model.id.in_(ids),
                        self._repository.model.created_by == user_id,
                    )
                    .all()
                )

                if len(dashboards) != len(ids):
                    raise ValueError(
                        "One or more dashboards not found or you don't have permission to delete them"
                    )

                # Delete all dashboards
                for dashboard in dashboards:
                    session.delete(dashboard)

                session.commit()
                return {
                    "message": f"Successfully deleted {len(dashboards)} dashboard(s)",
                    "deleted_count": len(dashboards),
                }

            except Exception:
                session.rollback()
                raise ValueError("Failed to delete dashboards")

    async def get_filter_configuration(self, index_type: str) -> Dict[str, Any]:
        """
        Get fields for dashboard filtering with supported filter types

        Args:
            index_type: Type of fields to return
                - 'common': Fields available across all indices (universal fields)
                - 'r085': Fields specific to R085 index
                - 'r025': Fields specific to R025 index

        Returns:
            Dictionary containing fields with their supported filter types
        """
        try:
            fields_data = get_filter_configuration_for_index(index_type)
            fields = []
            for field_key, field_info in fields_data.items():
                field_data = {
                    "field_name": field_info["field_name"],
                    "display_name": field_info["display_name"],
                    "field_type": field_info["field_type"],
                    "supported_filters": field_info["supported_filters"],
                    "is_universal": index_type == "common",
                }
                if index_type == "common":
                    field_data.update(
                        {
                            "compatible_indices": ["r085", "r025", "r085_v3"],
                            "type_compatibility": {
                                "compatible": True,
                                "indices": ["r085", "r025", "r085_v3"],
                            },
                            "is_mapped_field": True,
                        }
                    )
                else:
                    field_data.update(
                        {
                            "specific_to_index": index_type,
                        }
                    )
                fields.append(field_data)

            # Add common fields to index-specific requests
            if index_type != "common":
                from src.elasticsearch.constants import (
                    COMMON_FIELDS,
                    _enhance_field_info,
                )

                for field_key, field_info in COMMON_FIELDS.items():
                    field_data = {
                        "field_name": field_info["field_name"],
                        "display_name": field_info["display_name"],
                        "field_type": (
                            field_info["field_type"]
                            if "field_type" in field_info
                            else _enhance_field_info(field_info)["field_type"]
                        ),
                        "supported_filters": (
                            field_info["supported_filters"]
                            if "supported_filters" in field_info
                            else _enhance_field_info(field_info)["supported_filters"]
                        ),
                        "is_universal": True,
                        "compatible_indices": ["r085", "r025", "r085_v3"],
                        "type_compatibility": {
                            "compatible": True,
                            "indices": ["r085", "r025", "r085_v3"],
                        },
                        "is_mapped_field": True,
                    }
                    fields.append(field_data)

            description = f"Fields available for {index_type.upper()} index" + (
                " (including universal fields)" if index_type != "common" else ""
            )
            message = f"Successfully retrieved {len(fields)} fields for {index_type.upper()} index"

            return {
                "success": True,
                "data": {
                    "index_type": index_type,
                    "fields": fields,
                    "total_fields": len(fields),
                    "description": description,
                },
                "message": message,
            }

        except Exception:
            raise Exception(f"Error fetching fields for {index_type}")

    def save_dashboard_filters(
        self, dashboard_id: int, filters: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """
        Save filters to a dashboard

        Args:
            dashboard_id: ID of the dashboard to update
            filters: Filter configuration to save
            user_id: ID of the user making the request

        Returns:
            Updated dashboard information
        """
        try:
            # Update the filters
            with self._repository.session_factory() as session:
                db_dashboard = (
                    session.query(self._repository.model)
                    .filter_by(id=dashboard_id)
                    .first()
                )
                if not db_dashboard:
                    raise NotFoundError(
                        detail=f"Dashboard with ID {dashboard_id} not found"
                    )

                # Validate that user has permission to modify this dashboard
                if db_dashboard.created_by != user_id:
                    # Check if user has write access (dashboard is shared with them)
                    has_write_access = False
                    if db_dashboard.visibility == "SHARED":
                        for share in db_dashboard.shared_with:
                            if share.user_id == user_id:
                                has_write_access = True
                                break

                    if not has_write_access:
                        raise UnauthorizedError(
                            detail="You don't have permission to modify filters for this dashboard"
                        )

                # Save the filters
                db_dashboard.filters = filters
                session.commit()
                session.refresh(db_dashboard)

                return {
                    "success": True,
                    "message": "Dashboard filters saved successfully",
                    "data": {
                        "dashboard_id": dashboard_id,
                        "filters": db_dashboard.filters,
                        "updated_at": (
                            db_dashboard.updated_at.isoformat()
                            if db_dashboard.updated_at
                            else None
                        ),
                    },
                }

        except (NotFoundError, UnauthorizedError):
            raise
        except Exception:
            raise FailedToCreateError(detail="Error saving dashboard filters")
