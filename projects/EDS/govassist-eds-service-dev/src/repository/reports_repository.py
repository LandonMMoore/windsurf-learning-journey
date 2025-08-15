from typing import Any, Callable, List, Optional, TypeVar

from abs_nosql_repository_core.repository import BaseRepository as BaseNoSQLRepository
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from src.core.config import configs
from src.core.exceptions import InternalServerError, NotFoundError
from src.model.base_model import BaseModel
from src.model.nosql_document.ns_report_model import (
    FormulaAssistantChatHistory,
    ReportChatHistory,
)
from src.model.report_metadata_model import ReportMetadata
from src.model.report_model import ReportConfiguration, ReportTemplate, Tag
from src.mongodb.collections import (
    FORMULA_ASSISTANT_CHAT_HISTORY_COLLECTION,
    REPORT_CHAT_HISTORY_COLLECTION,
)
from src.repository.base_repository import BaseRepository
from src.schema.report_template_schema import ReportTemplateCreateExcludeTags
from src.util.get_field import get_field
from src.util.query_builder import (
    apply_ordering,
    apply_pagination,
    apply_search,
    dict_to_sqlalchemy_filter_options,
)

T = TypeVar("T", bound=BaseModel)


class ReportMetadataRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ReportMetadata)

    def read_by_options(
        self,
        schema: Any,
        searchable_fields: Optional[List[str]] = None,
        eager: bool = False,
    ) -> Any:
        schema_as_dict: dict = schema.dict(exclude_none=True)
        page = schema_as_dict.get("page", configs.PAGE)
        page_size = schema_as_dict.get("page_size", configs.PAGE_SIZE)
        ordering = schema_as_dict.get("ordering", configs.ORDERING)
        search_term = schema_as_dict.get("search")

        with self.session_factory() as session:
            query = session.query(self.model)

            if searchable_fields:
                query = apply_search(query, self.model, searchable_fields, search_term)

            query = apply_ordering(query, self.model, ordering)

            filter_dict = schema.dict(exclude_none=True)

            filter_dict.pop("search", None)
            filter_dict.pop("usage_tags", None)

            filter_options = dict_to_sqlalchemy_filter_options(self.model, filter_dict)
            query = query.filter(filter_options)
            if usage_tags := schema_as_dict.get("usage_tags"):
                query = query.filter(
                    self.model.usage_tags.like(f"%{usage_tags.value}%")
                )

            results, total_count = apply_pagination(query, page, page_size)
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


class ReportConfigurationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ReportConfiguration)

    def read_by_options(
        self,
        schema: T,
        searchable_fields: Optional[List[str]] = None,
        eager: bool = False,
        exclude_eagers: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
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
                        if field in {"tags", "tag"}:
                            query = query.filter(
                                self.model.tags_association.any(
                                    Tag.name.ilike(f"%{search_term}%")
                                )
                            )
                            continue
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

                if tags:
                    query = query.filter(
                        self.model.tags_association.any(Tag.name.in_(tags))
                    )

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
                logger.error(f"Error reading report configuration: {e}")
                raise InternalServerError()


class ReportTemplateRepository(BaseRepository):
    def __init__(
        self,
        session_factory: Callable[..., Session],
    ):
        super().__init__(session_factory, ReportTemplate)

    def read_by_options(
        self,
        schema: T,
        searchable_fields: Optional[List[str]] = None,
        eager: bool = False,
        exclude_eagers: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
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
                        if field in {"tags", "tag"}:
                            query = query.filter(
                                self.model.tags_association.any(
                                    Tag.name.ilike(f"%{search_term}%")
                                )
                            )
                            continue
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

                if tags:
                    query = query.filter(
                        self.model.tags_association.any(Tag.name.in_(tags))
                    )

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
                logger.error(f"Error reading report template: {e}")
                raise InternalServerError()

    def extract_report_template(self, schema: Any):
        with self.session_factory() as session:
            report_config = (
                session.query(ReportConfiguration)
                .filter(ReportConfiguration.id == schema.report_id)
                .options(selectinload(ReportConfiguration.sub_reports))
                .first()
            )
            if not report_config:
                raise NotFoundError(
                    detail=f"Report configuration with id {schema.report_id} not found"
                )
            sub_reports = report_config.sub_reports
            if not sub_reports:
                raise NotFoundError(
                    detail=f"No sub reports found for report configuration with id {schema.report_id}"
                )

            combined_config = []
            for sub_report in sub_reports:
                config = {
                    "name": sub_report.name,
                    "description": sub_report.description,
                    "config": sub_report.config,
                }
                combined_config.append(config)

            report_template = ReportTemplateCreateExcludeTags(
                name=schema.name,
                description=schema.description,
                config=combined_config,
                created_by_id=schema.created_by_id,
            )
            return self.create(report_template)


class TagRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, Tag)


class BaseChatHistoryRepository(BaseNoSQLRepository):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, document_model):
        self.collection_name = collection_name
        self.document_model = document_model
        super().__init__(document_model, db)

    async def get_next_chat_id(self):
        try:
            last_chat = await self.db.get_collection(self.collection_name).find_one(
                sort=[("chat_id", -1)]
            )
            if last_chat:
                return last_chat["chat_id"] + 1
            return 1
        except Exception as e:
            logger.error(f"Error getting next chat ID: {e}")
            raise InternalServerError("Error getting next chat ID.")

    async def check_if_chat_exists(self, chat_id: int, user_id: int):
        try:
            chat = await self.db.get_collection(self.collection_name).find_one(
                {"chat_id": chat_id}
            )
            return chat is not None
        except Exception as e:
            logger.error(f"Error checking if chat exists: {e}")
            raise InternalServerError("Error checking if chat exists.")

    async def check_if_message_exists(
        self, chat_id: int, message_id: int, user_id: int
    ):
        try:
            message = await self.db.get_collection(self.collection_name).find_one(
                {"chat_id": chat_id, "message_id": message_id}
            )
            return message is not None
        except Exception:
            logger.error("Error checking if message exists.")
            raise InternalServerError("Error checking if message exists.")

    async def get_next_message_id(self, chat_id: int, user_id: int):
        try:
            message = await self.db.get_collection(self.collection_name).find_one(
                {"chat_id": chat_id, "user_id": user_id}, sort=[("message_id", -1)]
            )
            if message:
                return message["message_id"] + 1
            return 1
        except Exception:
            logger.error("Error getting next message ID.")
            raise InternalServerError("Error getting next message ID.")

    async def get_message(self, chat_id: int, message_id: int, user_id: int):
        try:
            message = await self.db.get_collection(self.collection_name).find_one(
                {"chat_id": chat_id, "user_id": user_id, "message_id": message_id}
            )
            return message
        except Exception:
            logger.error("Error getting message.")
            raise InternalServerError("Error getting message.")

    async def get_chat_history(
        self, chat_id: int, user_id: int, limit: int = 10, message_id: int = None
    ):
        try:
            # TODO: Need to handle the case where message_id is provided.
            chat_history = (
                await self.db.get_collection(self.collection_name)
                .find({"chat_id": chat_id, "user_id": user_id})
                .sort([("message_id", 1)])
                .to_list(length=None)
            )

            # Convert ObjectId to string for JSON serialization
            for item in chat_history:
                if "_id" in item:
                    item["_id"] = str(item["_id"])

            return chat_history
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            raise InternalServerError("Error getting chat history.")


class ReportChatHistoryRepository(BaseChatHistoryRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, REPORT_CHAT_HISTORY_COLLECTION, ReportChatHistory)

    async def update_feedback(
        self, chat_id: int, user_id: int, message_id: int, feedback: str
    ):
        """Update feedback for a specific chat message"""
        try:
            result = await self.db.get_collection(self.collection_name).update_one(
                {"chat_id": chat_id, "user_id": user_id, "message_id": message_id},
                {"$set": {"feedback": feedback}},
            )

            if result.matched_count == 0:
                raise NotFoundError(
                    detail=f"Report chat history with chat_id {chat_id}, user_id {user_id}, message_id {message_id} not found"
                )

            return "Feedback updated successfully"
        except Exception as e:
            logger.error(f"Error updating feedback: {e}")
            raise InternalServerError("Error updating feedback")


class FormulaAssistantChatHistoryRepository(BaseChatHistoryRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(
            db, FORMULA_ASSISTANT_CHAT_HISTORY_COLLECTION, FormulaAssistantChatHistory
        )
