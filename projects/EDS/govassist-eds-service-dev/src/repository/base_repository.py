from contextlib import AbstractContextManager
from typing import Any, Callable, List, Optional, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import asc, desc, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Query, Session, joinedload, selectinload

from src.consts.sortDirection import SortDirection
from src.core.config import configs
from src.core.exceptions import DuplicatedError, NotFoundError, ValidationError
from src.model.base_model import BaseModel
from src.util.get_field import get_field
from src.util.query_builder import dict_to_sqlalchemy_filter_options

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        model: Type[T],
    ) -> None:
        self.session_factory = session_factory
        self.model = model

    def _build_sort_orders(self, sort_fields: List[str], query: Query) -> Any:
        orders = []
        # Track which joins have already been added to prevent duplicates
        existing_joins = set()

        for field_expr in sort_fields:
            if field_expr.startswith("-"):
                direction = SortDirection.DESC
                field = field_expr[1:]
            else:
                direction = SortDirection.ASC
                field = field_expr

            # Handle nested fields
            if "." in field:
                # Check if this join path has already been processed
                if field not in existing_joins:
                    query, column = get_field(self.model, field, query)
                    existing_joins.add(field)
                else:
                    # If join already exists, just get the column without modifying query
                    column = self._get_column_for_field(field)
            else:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                else:
                    raise ValidationError(
                        detail=f"Field '{field}' does not exist on model {self.model.__name__}"
                    )

            orders.append(
                desc(column) if direction == SortDirection.DESC else asc(column)
            )

        return query, orders

    def _get_column_for_field(self, field_name: str):
        """Get column for a nested field without modifying the query"""
        if "." not in field_name:
            return getattr(self.model, field_name)

        path_parts = field_name.split(".")
        current_model = self.model

        for part in path_parts[:-1]:
            relationship_attr = getattr(current_model, part)
            current_model = relationship_attr.property.mapper.class_

        return getattr(current_model, path_parts[-1])

    def read_by_options(
        self,
        schema: T,
        searchable_fields: Optional[List[str]] = None,
        eager: bool = False,
        exclude_eagers: Optional[List[str]] = None,
    ) -> dict:
        with self.session_factory() as session:
            try:
                schema_as_dict: dict = schema.dict(exclude_none=True)

                if isinstance(searchable_fields, str):
                    searchable_fields = [searchable_fields]

                if searchable_fields is None and schema_as_dict.get("search"):
                    searchable_fields = ["name"]

                ordering: str = schema_as_dict.get("ordering", configs.ORDERING)

                page = schema_as_dict.get("page", configs.PAGE)
                page_size = schema_as_dict.get("page_size", configs.PAGE_SIZE)
                search_term = schema_as_dict.get("search")
                query = session.query(self.model)

                if eager:
                    eagers = getattr(self.model, "eagers", [])
                    if exclude_eagers:
                        eagers = [
                            eager for eager in eagers if eager not in exclude_eagers
                        ]

                    for relation_path in eagers:
                        path_parts = relation_path.split(".")
                        current_class = self.model
                        current_attr = getattr(current_class, path_parts[0])
                        loader = selectinload(current_attr)

                        for part in path_parts[1:]:
                            current_class = current_attr.property.mapper.class_
                            current_attr = getattr(current_class, part)
                            loader = loader.selectinload(current_attr)

                        query = query.options(loader)

                filter_dict = schema.dict(exclude_none=True)
                if "search" in filter_dict:
                    del filter_dict["search"]
                filter_options = dict_to_sqlalchemy_filter_options(
                    self.model, filter_dict
                )

                query = query.filter(filter_options)
                if searchable_fields and search_term:
                    search_filters = []
                    # Track which joins have already been added to prevent duplicates
                    existing_joins = set()

                    for field in searchable_fields:
                        if "." in field:
                            if field not in existing_joins:
                                query_with_joins, column = get_field(
                                    self.model, field, query
                                )
                                # Update the query with the joins if they were added
                                if query_with_joins is not query:
                                    query = query_with_joins
                                existing_joins.add(field)
                            else:
                                # If join already exists, just get the column without modifying query
                                column = self._get_column_for_field(field)
                            search_filters.append(column.ilike(f"%{search_term}%"))
                        else:
                            if hasattr(self.model, field):
                                search_filters.append(
                                    getattr(self.model, field).ilike(f"%{search_term}%")
                                )
                    if search_filters:
                        query = query.filter(or_(*search_filters))

                if ordering:
                    ordering_list = ordering.split(",")
                    query, sort_query = self._build_sort_orders(ordering_list, query)
                    query = query.order_by(*sort_query)
                else:
                    query = query.order_by(self.model.id.desc())

                total_count = query.count()
                if page_size == "all":
                    results = query.all()
                else:
                    page_size = int(page_size)
                    results = (
                        query.limit(page_size).offset((page - 1) * page_size).all()
                    )
                return {
                    "founds": results,
                    "search_options": {
                        "page": page,
                        "page_size": page_size,
                        "ordering": ordering,
                        "total_count": total_count,
                        "search_term": search_term,
                    },
                }
            except SQLAlchemyError as e:
                raise ValidationError(detail=str(e))

    def read_by_id(self, id: int, eager: bool = False):
        with self.session_factory() as session:
            try:
                query = session.query(self.model)
                if eager:
                    for relation_path in getattr(self.model, "eagers", []):
                        path_parts = relation_path.split(".")
                        current_class = self.model
                        current_attr = getattr(current_class, path_parts[0])
                        loader = joinedload(current_attr)

                        for part in path_parts[1:]:
                            current_class = current_attr.property.mapper.class_
                            current_attr = getattr(current_class, part)
                            loader = loader.joinedload(current_attr)

                        query = query.options(loader)
                query = query.filter(self.model.id == id).first()
                if not query:
                    raise NotFoundError(detail=f"not found id : {id}")
                return query
            except SQLAlchemyError as e:
                raise ValidationError(detail=str(e))

    def create(self, schema: T):
        with self.session_factory() as session:
            query = self.model(**schema.model_dump())
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
                query = self.read_by_id(query.id, eager=True)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            except SQLAlchemyError as e:
                raise ValidationError(detail=str(e))
            return query

    def update(
        self, id: int, schema: T, exclude_none: bool = True, exclude_unset: bool = False
    ):
        with self.session_factory() as session:
            try:
                # Apply updates
                affected_rows = (
                    session.query(self.model)
                    .filter(self.model.id == id)
                    .update(
                        schema.model_dump(
                            exclude_none=exclude_none, exclude_unset=exclude_unset
                        ),
                        synchronize_session="fetch",
                    )
                )
                if not affected_rows:
                    raise NotFoundError(detail=f"not found id : {id}")
                session.commit()

                # Fetch updated record WITH RELATIONSHIPS loaded
                query = self.read_by_id(id, eager=True)

                return query  # FastAPI will serialize correctly

            except IntegrityError as e:
                session.rollback()
                raise DuplicatedError(detail=str(e.orig))
            except SQLAlchemyError as e:
                session.rollback()
                raise ValidationError(detail=str(e))

    def update_attr(self, id: int, column: str, value: Any):
        with self.session_factory() as session:
            try:
                session.query(self.model).filter(self.model.id == id).update(
                    {column: value}
                )
                session.commit()
                return self.read_by_id(id, eager=True)
            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=str(e))

    def whole_update(self, id: int, schema: T):
        with self.session_factory() as session:
            try:
                session.query(self.model).filter(self.model.id == id).update(
                    schema.dict()
                )
                session.commit()
                return self.read_by_id(id, eager=True)
            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=str(e))

    def delete_by_id(self, id: int):
        with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.id == id).first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            try:
                session.delete(query)
                session.commit()
            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=str(e))

    def get_unique_values(self, schema: Any) -> Any:
        """Get unique values for a specific field"""
        field_name = schema.field_name
        search = schema.search
        page = schema.page or 1  # Default to page 1 if not provided
        page_size = schema.page_size or 20  # Default to 20 if not provided
        ordering = schema.ordering or "-id"  # Default to -id if not provided

        # Get the model class
        model_class = self.model

        with self.session_factory() as session:
            # Start building the query
            field = getattr(model_class, field_name)

            # First get distinct values
            subquery = session.query(field).distinct()

            # Apply search filter if provided
            if search:
                subquery = subquery.filter(field.ilike(f"%{search}%"))

            # Get total count
            total_count = subquery.count()

            # Apply ordering to the distinct values
            if ordering.startswith("-"):
                subquery = subquery.order_by(field.desc())
            else:
                subquery = subquery.order_by(field.asc())

            # Apply pagination
            if page_size != "all":
                page_size = int(page_size)
                subquery = subquery.offset((page - 1) * page_size).limit(page_size)

            # Get the final results
            unique_values = [value[0] for value in subquery.all()]

            return {
                "founds": unique_values,
                "search_options": {
                    "ordering": ordering,
                    "page": page,
                    "page_size": page_size,
                    "search": search,
                    "total_count": total_count,
                },
            }

    def close_scoped_session(self):
        with self.session_factory() as session:
            return session.close()
