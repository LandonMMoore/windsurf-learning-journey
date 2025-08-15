from typing import Callable

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from src.repository.fhwa_repository import FhwaRepository
from src.schema.fhwa_schema import FhwaFind
from src.services.base_service import BaseService


class FhwaService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(FhwaRepository(session_factory))

    def filter_null_values(self, field_name: str, find: FhwaFind):
        # Initialize schema with default pagination and ordering if not provided
        schema = FhwaFind(
            page=find.page or 1,
            page_size=find.page_size or 20,
            ordering=find.ordering or "-id",
            search=find.search,
        )

        # Validate the field name
        if not hasattr(self._repository.model, field_name):
            raise ValueError(f"Invalid field name: {field_name}")

        # Get the field attribute from the SQLAlchemy model
        field = getattr(self._repository.model, field_name)

        # Build filter condition to exclude None, empty string, and "null" string
        filter_condition = and_(field.isnot(None), field != "", field != "null")

        with self._repository.session_factory() as session:
            query = session.query(self._repository.model).filter(filter_condition)

            # Count total records before applying pagination
            total_count = query.count()

            # Apply ordering if needed
            if schema.ordering == "-id":
                query = query.order_by(desc(self._repository.model.id))
            elif schema.ordering == "id":
                query = query.order_by(self._repository.model.id)

            # Apply pagination if page_size is not "all"
            page = schema.page
            page_size = schema.page_size
            if str(page_size).lower() != "all":
                page_size = int(page_size)
                query = query.limit(page_size).offset((page - 1) * page_size)

            results = query.all()

            return {
                "founds": results,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": schema.ordering,
                    "total_count": total_count,
                    "search_term": schema.search,
                },
            }
