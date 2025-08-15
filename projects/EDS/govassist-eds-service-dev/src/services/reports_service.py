import logging
from datetime import UTC
from datetime import datetime as dt
from datetime import timedelta as td
from typing import Any, Callable

from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.config import configs
from src.core.exceptions import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)
from src.core.extensions import blob_service_client
from src.elasticsearch.service import es_service
from src.model.master_model import (
    MasterAward,
    MasterCostCenter,
    MasterFund,
    MasterParentTask,
    MasterProgram,
    MasterProjectDetails,
    MasterSponsor,
    MasterSubTask,
    MasterTransaction,
)
from src.model.report_model import (
    ReportConfiguration,
    ReportConfigurationTagAssociation,
    ReportExport,
    ReportTemplate,
    ReportTemplateTagAssociation,
    Tag,
)
from src.model.sub_report_model import SubReport
from src.repository.base_repository import BaseRepository
from src.repository.reports_repository import (
    FormulaAssistantChatHistoryRepository,
    ReportChatHistoryRepository,
    ReportConfigurationRepository,
    ReportMetadataRepository,
    ReportTemplateRepository,
    TagRepository,
)
from src.schema.report_schema import (
    OPERATOR_DATA_TYPE_MAP,
    MasterModelUniqueValues,
    ReportAgentResponseFeedback,
    ReportConfigurationQueryElasticsearch,
    ReportFind,
    SubReportConfigBaseSchema,
)
from src.services.base_service import BaseService
from src.services.redis_service import RedisService
from src.util.get_fields_from_models import get_fields_from_models
from src.util.reports import (
    TABLE_CONFIG,
    build_filter_condition,
    build_sqlalchemy_query,
    make_report_redis_key,
    resolve_join_chain,
)
from src.tasks.report_export import report_export
logger = logging.getLogger(__name__)
from celery.exceptions import TimeoutError as CeleryTimeoutError
from kombu.exceptions import OperationalError


class ReportMetadataService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(ReportMetadataRepository(session_factory))


class ReportConfigurationService(BaseService):

    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(ReportConfigurationRepository(session_factory))

    def add(self, schema, user_id: int):
        with self._repository.session_factory() as session:
            report_config = schema.model_dump()
            report_exists = (
                session.query(self._repository.model)
                .filter(self._repository.model.name == report_config.get("name"))
                .first()
            )
            if report_exists:
                raise ValidationError(
                    detail=f"Report with name {report_config.get('name')} already exists"
                )
            tags = report_config.pop("tags", None)
            tags_in_db = []
            if tags:
                tags_in_db = session.query(Tag).filter(Tag.id.in_(tags)).all()
                missing_tags = set(tags) - set(tag.id for tag in tags_in_db)
                if missing_tags:
                    raise ValidationError(
                        detail=f"Tags with ids {missing_tags} not found"
                    )
            template_id = report_config.get("template_id", None)
            if template_id is not None:
                template = (
                    session.query(ReportTemplate)
                    .filter(ReportTemplate.id == template_id)
                    .first()
                )
                if not template:
                    raise ValidationError(
                        detail=f"Template with id {template_id} not found"
                    )
            query = self._repository.model(**report_config, created_by_id=user_id)
            query.tags_association = [
                ReportConfigurationTagAssociation(report_configuration=query, tag=tag)
                for tag in tags_in_db
            ]
            session.add(query)
            session.commit()
            session.refresh(query)
            query = self._repository.read_by_id(query.id, eager=True)
            return query

    def patch(self, report_id: int, schema):
        with self._repository.session_factory() as session:
            report_config = schema.model_dump(exclude_unset=True)
            report = (
                session.query(self._repository.model)
                .filter(self._repository.model.id == report_id)
                .first()
            )
            if not report:
                raise ValidationError(detail=f"Report with id {report_id} not found")

            if "name" in report_config:
                report_exists = (
                    session.query(self._repository.model)
                    .filter(
                        self._repository.model.name == report_config["name"],
                        self._repository.model.id != report_id,
                    )
                    .first()
                )
                if report_exists:
                    raise ValidationError(
                        detail=f"Report with name {report_config['name']} already exists"
                    )
            tags = report_config.pop("tags", None)
            tags_in_db = []
            if tags is not None:
                tags_in_db = session.query(Tag).filter(Tag.id.in_(tags)).all()
                missing_tags = set(tags) - set(tag.id for tag in tags_in_db)
                if missing_tags:
                    raise ValidationError(
                        detail=f"Tags with ids {missing_tags} not found"
                    )
                session.query(ReportConfigurationTagAssociation).filter_by(
                    report_configuration_id=report.id
                ).delete()
                if tags_in_db:
                    tags_association = [
                        ReportConfigurationTagAssociation(
                            report_configuration_id=report.id, tag_id=tag.id
                        )
                        for tag in tags_in_db
                    ]
                    session.add_all(tags_association)

            if "template_id" in report_config:
                if report_config["template_id"] is not None:
                    template = (
                        session.query(ReportTemplate)
                        .filter(ReportTemplate.id == report_config["template_id"])
                        .first()
                    )
                    if not template:
                        raise ValidationError(
                            detail=f"Template with id {report_config['template_id']} not found"
                        )
                    report.template_id = template.id
                else:
                    report.template_id = None

            for field, value in report_config.items():
                setattr(report, field, value)
            session.commit()
            return self._repository.read_by_id(report_id, eager=True)

    def remove_by_id(self, report_id: int):
        with self._repository.session_factory() as session:
            query = (
                session.query(self._repository.model)
                .filter(self._repository.model.id == report_id)
                .first()
            )
            if not query:
                raise NotFoundError(detail=f"not found id : {report_id}")
            try:
                session.query(ReportConfigurationTagAssociation).filter_by(
                    report_configuration_id=query.id
                ).delete(synchronize_session=False)
                session.query(ReportConfiguration).filter_by(id=report_id).delete(
                    synchronize_session=False
                )
                session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Error deleting report: {e}")
                raise InternalServerError()

    def get_list(self, schema, searchable_fields, tags):
        return self._repository.read_by_options(
            schema,
            searchable_fields,
            eager=True,
            tags=tags,
            exclude_eagers=["sub_reports"],
        )

    def get_fields(self, searchable_fields, search=None, ordering="column_name"):
        common_exclude_fields = {"deleted_at", "created_at", "updated_at", "uuid", "id"}
        TABLE_CONFIG = {
            "master_funds": {
                "model": MasterFund,
                "exclude_fields": common_exclude_fields,
            },
            "master_programs": {
                "model": MasterProgram,
                "exclude_fields": common_exclude_fields,
            },
            "master_cost_centers": {
                "model": MasterCostCenter,
                "exclude_fields": common_exclude_fields,
            },
            # "master_accounts": {
            #     "model": MasterAccount,
            #     "exclude_fields": common_exclude_fields,
            # },
            "master_project_details": {
                "model": MasterProjectDetails,
                "exclude_fields": common_exclude_fields,
            },
            "master_awards": {
                "model": MasterAward,
                "exclude_fields": common_exclude_fields,
            },
            "master_sponsors": {
                "model": MasterSponsor,
                "exclude_fields": common_exclude_fields,
            },
            "master_parent_tasks": {
                "model": MasterParentTask,
                "exclude_fields": common_exclude_fields,
            },
            "master_sub_tasks": {
                "model": MasterSubTask,
                "exclude_fields": common_exclude_fields,
            },
            "master_transactions": {
                "model": MasterTransaction,
                "exclude_fields": common_exclude_fields,
            },
        }
        return get_fields_from_models(TABLE_CONFIG, searchable_fields, search, ordering)

    async def data_query(self, query: ReportConfigurationQueryElasticsearch):
        try:
            # Get the index mapping to determine field types
            mapping_info = await es_service.get_index_mapping(query.index)
            query_filter = es_service.build_filter_clause(
                query.filter, query.index, mapping_info
            )

            query_search = es_service.build_search_clause(query.search, mapping_info)
            query_sort = es_service.build_sort_clause(
                query.sort, query.index, mapping_info
            )

            es_query = es_service.build_es_query(
                query_filter,
                query_search,
                query_sort,
                query.page,
                query.page_size,
                query.index,
            )

            logger.debug(f"Executing ES query: {es_query}")
            response = await es_service.es_query_executor(query.index, es_query)
            return response

        except Exception as e:
            logger.error(f"Error executing Elasticsearch query: {str(e)}")
            raise InternalServerError(detail="Failed to execute Elasticsearch query")

    def get_shared_data(self, schema_name: str, find=None, searchable_fields=None):

        model_class = TABLE_CONFIG[schema_name]
        data_repository = BaseRepository(self._repository.session_factory, model_class)
        return data_repository.read_by_options(find, searchable_fields, eager=True)

    def get_report_functions(self):
        return [
            # Numeric Functions
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "SUM",
                "description": "Sum up all the given numbers",
                "example": "SUM({sub_task.award_funding_amount}, {sub_task.commitment})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "MAX",
                "description": "Returns the largest value from a set of data",
                "example": "MAX({sub_task.award_funding_amount}, {sub_task.commitment}, {sub_task.obligation})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "MIN",
                "description": "Returns the smallest value from a set of data",
                "example": "MIN({sub_task.award_funding_amount}, {sub_task.commitment}, {sub_task.obligation})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "AVERAGE",
                "description": "Calculates the average of a set of numbers",
                "example": "AVERAGE({sub_task.award_funding_amount}, {sub_task.commitment}, {sub_task.obligation})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "MOD",
                "description": "Returns the remainder after dividing one number by another",
                "example": "MOD({transaction.transaction_amount}, {transaction.burdened_amount})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "ROUND",
                "description": "Rounds a number to a specified number of decimal places",
                "example": "ROUND({transaction.rate}, 2)",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "CEIL",
                "description": "Rounds a number up to the nearest integer",
                "example": "CEIL({transaction.rate})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "FLOOR",
                "description": "Rounds a number down to the nearest integer",
                "example": "FLOOR({transaction.quantity})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "LOG",
                "description": "Returns the logarithm of a number",
                "example": "LOG({transaction.burdened_amount})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "SQRT",
                "description": "Positive square root of a positive number",
                "example": "SQRT({transaction.burdened_amount})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "POWER",
                "description": "A number raised to a power",
                "example": "POWER({transaction.quantity}, 2)",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Numeric",
                "display_name": "ABS",
                "description": "Absolute value of a number",
                "example": "ABS({transaction.quantity})",
            },
            # Date & Time Functions
            {
                "category": "Functions & Constants",
                "sub_category": "Date & Time",
                "display_name": "DATEDIFF",
                "description": "Returns the number of days between two dates",
                "example": "DATEDIFF('day', {sub_task.start_date}, {sub_task.completion_date})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Date & Time",
                "display_name": "DATEADD",
                "description": "Adds a specified number of days to a date",
                "example": "DATEADD('day', 10, {sub_task.start_date})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Date & Time",
                "display_name": "DATEPART",
                "description": "Extracts a specific part of a date",
                "example": "DATEPART('year', {sub_task.start_date})",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Date & Time",
                "display_name": "TODAY",
                "description": "Returns the current date",
                "example": "TODAY()",
            },
            # Conditional Functions
            {
                "category": "Functions & Constants",
                "sub_category": "Conditionals",
                "display_name": "IF",
                "description": "Returns one value if a condition is true and another value if it is false",
                "example": "IF({sub_task.award_funding_amount} > 1000, 'Yes', 'No')",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Conditionals",
                "display_name": "AND",
                "description": "Returns true if all conditions are true",
                "example": "IF({sub_task.award_funding_amount} > 1000 AND {sub_task.commitment} > 1000, 'Yes', 'No')",
            },
            {
                "category": "Functions & Constants",
                "sub_category": "Conditionals",
                "display_name": "OR",
                "description": "Evaluates to true if any of the conditions is true.",
                "example": "IF({sub_task.award_funding_amount} > 1000 OR {sub_task.commitment} > 1000, 'Yes', 'No')",
            },
        ]

    def build_preview_response(
        self, report_config: dict, result, page=1, page_size=10, total_count=0
    ):
        config_fields = report_config["config"]

        # Extract field labels
        fields_by_uuid = {
            field["uuid"]: {"uuid": field["uuid"], "label": field["label"]}
            for field in config_fields
        }

        # Paginate result
        total_pages = max(1, (total_count + page_size - 1) // page_size)

        # Build row data
        founds = []
        for row in result:
            found_row = {}
            for field_uuid, field_info in fields_by_uuid.items():
                data = getattr(row, field_uuid, None)
                found_row[field_info["uuid"]] = data

            founds.append(found_row)

        # Build response
        return {
            "fields": list(fields_by_uuid.values()),
            "founds": founds,
            "search_options": {
                "total_pages": total_pages,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "search": None,
                "sort_order": [],
            },
        }

    async def preview_report(
        self,
        report_id: int,
        sub_report_id: int,
        find: ReportFind,
        redis_service: RedisService,
    ):
        with self._repository.session_factory() as session:
            report = (
                session.query(self._repository.model)
                .filter(self._repository.model.id == report_id)
                .first()
            )
            if not report:
                raise NotFoundError(detail=f"Report with id {report_id} not found")

            sub_report = (
                session.query(SubReport)
                .filter(
                    SubReport.id == sub_report_id,
                    SubReport.report_configuration_id == report_id,
                )
                .first()
            )
            if not sub_report:
                raise NotFoundError(
                    detail=f"Sub report with id {sub_report_id} not found"
                )

            sub_report_config = sub_report.config
            if not sub_report_config:
                raise NotFoundError(detail="Sub report config not present.")

            find_dict = find.model_dump()
            try:
                sub_report_config["filters"] = find_dict["filters"]
                SubReportConfigBaseSchema.model_validate(sub_report_config)
            except Exception as e:
                logger.error(f"Error validating report config: {e}")
                raise ValidationError(detail=str(e))

            try:
                redis_key = make_report_redis_key(
                    report_id, sub_report_id, sub_report_config
                )
                cached_result = await redis_service.cache_get(redis_key)
                if (
                    cached_result is not None
                    and "db_query" in cached_result
                    and "count_query" in cached_result
                ):
                    raw_sql = cached_result["db_query"]
                    count_sql = cached_result["count_query"]

                else:
                    base, join_plan = resolve_join_chain(
                        sub_report_config["config"], sub_report_config["group_by"]
                    )
                    # For now we are not supporting ordering in the preview API, So by default data will be ordered by id of the base table.
                    stmt, count_stmt, data_type_map, formula_map = (
                        build_sqlalchemy_query(
                            session, sub_report_config, base, join_plan, None
                        )
                    )

                    filter_expr = build_filter_condition(
                        sub_report_config["filters"], data_type_map, formula_map
                    )
                    if filter_expr is not None:
                        stmt = stmt.where(filter_expr)
                        count_stmt = count_stmt.where(filter_expr)

                    count_sql = f"SELECT COUNT(*) FROM ({count_stmt.compile(compile_kwargs={'literal_binds': True})}) AS subquery"

                    raw_sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

                    await redis_service.cache_set(
                        redis_key,
                        {
                            "db_query": raw_sql,
                            "count_query": str(count_sql),
                            "field_types": data_type_map,
                        },
                        7200,
                    )

                # NOTE: The sql in the redis cache is already generated by the sqlalchemy query builder , So there we don't have issue with sql injection
                # and here we are just adding the pagination to the sql string.
                # NOTE: This is for mssql server.
                paginated_sql = f"""
                    {raw_sql}
                    OFFSET {(find.page - 1) * int(find.page_size)} ROWS
                    FETCH NEXT {int(find.page_size)} ROWS ONLY
                """

                result = session.execute(text(paginated_sql)).fetchall()
                count = session.execute(text(count_sql)).scalar()

                return self.build_preview_response(
                    sub_report_config, result, find.page, int(find.page_size), count
                )

            except Exception as e:
                logger.error(f"Error building join plan: {e}", exc_info=True)
                raise ValidationError(detail=f"Error building join plan: {e}")

    async def export_report(self, report_id: int, current_user_id: int):
        with self._repository.session_factory() as session:
            report = (
                session.query(ReportConfiguration)
                .filter(ReportConfiguration.id == report_id)
                .first()
            )
            if not report:
                raise NotFoundError(detail=f"Report with id {report_id} not found")

            # Check if the report is already being exported
            export = (
                session.query(ReportExport)
                .filter(
                    ReportExport.report_id == report_id,
                    ReportExport.status.in_(["PENDING", "IN_PROGRESS"]),
                )
                .first()
            )
            if export:
                one_day_ago = dt.now(UTC) - td(days=1)
                if export.created_at >= one_day_ago:
                    # Still within 1 day → block export
                    raise BadRequestError(detail="Report is already being exported.")
                else:
                    # More than 1 day old → delete it
                    logger.warning(f"Deleting stale export {export.id} for report {report_id}")
                    session.delete(export)
                    session.commit()

            # Create a new export
            export = ReportExport(report_id=report_id, created_by_id=current_user_id)
            session.add(export)
            session.commit()
            session.refresh(export)
            
            try:
                result = report_export.apply_async(args=[export.id])
                logger.info(f"Queued report export task: {result.id}")
            except (OperationalError, CeleryTimeoutError) as e:
                logger.error(f"Failed to queue report export: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "message": "Task queue is temporarily unavailable"
                    },
                )
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Export request received. Please check back later for the status."
                },
            )

    async def export_status(self, report_id: int):
        with self._repository.session_factory() as session:
            export = (
                session.query(ReportExport)
                .filter(ReportExport.report_id == report_id)
                .order_by(ReportExport.id.desc())
                .first()
            )
            if not export:
                raise NotFoundError(detail=f"Export not found for report {report_id}")

            res = {
                "status": export.status,
                "file_url": None,
                "stale_at": export.stale_at,
            }
            if export.status == "COMPLETED" and export.file_name:
                sas_token = generate_blob_sas(
                    account_name=blob_service_client.account_name,
                    container_name=configs.AZURE_STORAGE_CONTAINER_NAME,
                    blob_name=export.file_name,
                    account_key=blob_service_client.credential.account_key,  # Only works if using key credential
                    permission=BlobSasPermissions(read=True),
                    expiry=dt.now(UTC) + td(hours=1),
                )
                res["file_url"] = (
                    f"https://{blob_service_client.account_name}.blob.core.windows.net/{configs.AZURE_STORAGE_CONTAINER_NAME}/{export.file_name}?{sas_token}"
                )
            return res

    def get_supported_data_types(self):
        return {
            operator: list(types) for operator, types in OPERATOR_DATA_TYPE_MAP.items()
        }

    def get_master_table_unique_values(self, schema: MasterModelUniqueValues):
        try:
            if schema.schema_name not in TABLE_CONFIG:
                raise ValidationError(detail=f"Schema '{schema.schema_name}' not found")

            model_class = TABLE_CONFIG[schema.schema_name]
            data_repository = BaseRepository(
                self._repository.session_factory, model_class
            )

            if not hasattr(model_class, schema.field_name):
                raise ValidationError(
                    detail=f"Field '{schema.field_name}' not found in table '{schema.schema_name}'"
                )

            return data_repository.get_unique_values(schema)

        except ValidationError:
            raise
        except Exception:
            logger.error("Error getting unique values for field")
            raise InternalServerError(detail="Failed to retrieve unique values")

    def get_master_data_source_list(self):
        return [
            {"display_name": "Fund", "schema_name": "master_funds"},
            {"display_name": "Program", "schema_name": "master_programs"},
            {"display_name": "Cost Center", "schema_name": "master_cost_centers"},
            {"display_name": "Account", "schema_name": "master_accounts"},
            {"display_name": "Project", "schema_name": "master_project_details"},
            {"display_name": "Award", "schema_name": "master_awards"},
            {"display_name": "Sponsor", "schema_name": "master_sponsors"},
            {"display_name": "Parent Task", "schema_name": "master_parent_tasks"},
            {"display_name": "Sub Task", "schema_name": "master_sub_tasks"},
            {"display_name": "Transaction", "schema_name": "master_transactions"},
        ]

    def get_sub_report(self, sub_report_id: int):
        with self._repository.session_factory() as session:
            sub_report = (
                session.query(SubReport).filter(SubReport.id == sub_report_id).first()
            )
            if not sub_report:
                return None
            return sub_report


class ReportTemplateService(BaseService):
    def __init__(
        self,
        session_factory: Callable[..., Session],
    ):
        super().__init__(ReportTemplateRepository(session_factory))

    def add(self, schema):
        with self._repository.session_factory() as session:
            template_data = schema.model_dump()
            template_exists = (
                session.query(self._repository.model)
                .filter(self._repository.model.name == template_data.get("name"))
                .first()
            )
            if template_exists:
                raise ValidationError(
                    detail=f"Template with name {template_data.get('name')} already exists"
                )
            tags = template_data.pop("tags", None)
            tags_in_db = []
            if tags:
                tags_in_db = session.query(Tag).filter(Tag.id.in_(tags)).all()
                missing_tags = set(tags) - set(tag.id for tag in tags_in_db)
                if missing_tags:
                    raise ValidationError(
                        detail=f"Tags with ids {missing_tags} not found"
                    )
            query = self._repository.model(**template_data)
            query.tags_association = [
                ReportTemplateTagAssociation(report_template=query, tag=tag)
                for tag in tags_in_db
            ]
            session.add(query)
            session.commit()
            session.refresh(query)
            query = self._repository.read_by_id(query.id, eager=True)
            return query

    def patch(self, template_id: int, schema):
        with self._repository.session_factory() as session:
            template_data = schema.model_dump(exclude_unset=True)
            template = (
                session.query(self._repository.model)
                .filter(self._repository.model.id == template_id)
                .first()
            )
            if not template:
                raise NotFoundError(detail=f"Template with id {template_id} not found")

            if template.is_predefined:
                raise BadRequestError(
                    detail="This report template is predefined and cannot be changed."
                )

            if "name" in template_data:
                template_exists = (
                    session.query(self._repository.model)
                    .filter(
                        self._repository.model.name == template_data["name"],
                        self._repository.model.id != template_id,
                    )
                    .first()
                )
                if template_exists:
                    raise ValidationError(
                        detail=f"Template with name {template_data['name']} already exists"
                    )
            tags = template_data.pop("tags", None)
            tags_in_db = []
            if tags is not None:
                tags_in_db = session.query(Tag).filter(Tag.id.in_(tags)).all()
                missing_tags = set(tags) - set(tag.id for tag in tags_in_db)
                if missing_tags:
                    raise ValidationError(
                        detail=f"Tags with ids {missing_tags} not found"
                    )
                session.query(ReportTemplateTagAssociation).filter_by(
                    report_template_id=template.id
                ).delete()
                if tags_in_db:
                    tags_association = [
                        ReportTemplateTagAssociation(
                            report_template_id=template.id, tag_id=tag.id
                        )
                        for tag in tags_in_db
                    ]
                    session.add_all(tags_association)

            for key, value in template_data.items():
                setattr(template, key, value)
            session.commit()
            session.refresh(template)
            template = self._repository.read_by_id(template.id, eager=True)
            return template

    def extract_report_template(self, schema: Any):
        return self._repository.extract_report_template(schema)

    def get_list(self, schema, searchable_fields, tags):
        return self._repository.read_by_options(
            schema, searchable_fields, eager=True, tags=tags
        )

    def delete_report_template(self, report_template_id: int):
        with self._repository.session_factory() as session:
            report_template = (
                session.query(self._repository.model)
                .filter_by(id=report_template_id)
                .first()
            )
            if not report_template:
                raise NotFoundError(
                    detail=f"Report template with id {report_template_id} not found"
                )
            if report_template.is_predefined:
                raise BadRequestError(
                    detail="This report template is predefined and cannot be deleted."
                )
            return self._repository.delete_by_id(report_template_id)


class TagService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(TagRepository(session_factory))

    def get_or_create_tags(self, tag_names: list[str]):
        try:
            with self._repository.session_factory() as session:
                tags = session.query(Tag).filter(Tag.name.in_(tag_names)).all()
                missing_tags = set(tag_names) - set(tag.name for tag in tags)
                missing_tags_list = []
                for tag_name in missing_tags:
                    new_tag = Tag(name=tag_name)
                    session.add(new_tag)
                    missing_tags_list.append(new_tag)
                session.commit()
                # Refresh the newly created tags to get their IDs
                for new_tag in missing_tags_list:
                    session.refresh(new_tag)
                # Return tag IDs instead of Tag objects to avoid session binding issues
                all_tags = tags + missing_tags_list
                return [{"id": tag.id, "name": tag.name} for tag in all_tags]
        except Exception as e:
            logger.error(f"Error getting or creating tags: {e}")
            raise InternalServerError(detail="Error getting or creating tags")


class ReportChatHistoryService(BaseService):
    def __init__(self, report_chat_history_repository: ReportChatHistoryRepository):
        super().__init__(report_chat_history_repository)

    async def add(self, schema: Any):
        return await self._repository.create(schema)

    async def update(self, parent_message_object_id: str, data: dict):
        return await self._repository.update(parent_message_object_id, data)

    async def get_next_chat_id(self):
        return await self._repository.get_next_chat_id()

    async def check_if_chat_exists(self, chat_id: int, user_id: int):
        return await self._repository.check_if_chat_exists(chat_id, user_id)

    async def check_if_message_exists(
        self, chat_id: int, message_id: int, user_id: int
    ):
        return await self._repository.check_if_message_exists(
            chat_id, message_id, user_id
        )

    async def get_next_message_id(self, chat_id: int, user_id: int):
        return await self._repository.get_next_message_id(chat_id, user_id)

    async def get_message(self, chat_id: int, message_id: int, user_id: int):
        return await self._repository.get_message(chat_id, message_id, user_id)

    async def get_chat_history(
        self, chat_id: int, user_id: int, limit: int = 10, message_id: int = None
    ):
        return await self._repository.get_chat_history(
            chat_id, user_id, limit, message_id
        )

    async def report_agent_response_feedback(
        self, response_feedback: ReportAgentResponseFeedback, user_id: int
    ):
        """Update feedback for a specific chat message"""
        try:
            message = await self._repository.get_message(
                response_feedback.chat_id, response_feedback.message_id, user_id
            )
            if not message:
                raise NotFoundError(
                    detail=f"Report chat history with chat_id {response_feedback.chat_id}, user_id {user_id}, message_id {response_feedback.message_id} not found"
                )

            return await self._repository.update_feedback(
                response_feedback.chat_id,
                user_id,
                response_feedback.message_id,
                response_feedback.feedback,
            )

        except (NotFoundError, BadRequestError):
            raise
        except Exception as e:
            logger.error(f"Error updating feedback: {e}")
            raise InternalServerError(detail="Failed to update feedback")


class FormulaAssistantChatHistoryService(BaseService):
    def __init__(
        self,
        formula_assistant_chat_history_repository: FormulaAssistantChatHistoryRepository,
    ):
        super().__init__(formula_assistant_chat_history_repository)

    async def add(self, schema: Any):
        return await self._repository.create(schema)

    async def update(self, parent_message_object_id: str, data: dict):
        return await self._repository.update(parent_message_object_id, data)

    async def get_next_chat_id(self):
        return await self._repository.get_next_chat_id()

    async def check_if_chat_exists(self, chat_id: int, user_id: int):
        return await self._repository.check_if_chat_exists(chat_id, user_id)

    async def check_if_message_exists(
        self, chat_id: int, message_id: int, user_id: int
    ):
        return await self._repository.check_if_message_exists(
            chat_id, message_id, user_id
        )

    async def get_next_message_id(self, chat_id: int, user_id: int):
        return await self._repository.get_next_message_id(chat_id, user_id)

    async def get_message(self, chat_id: int, message_id: int, user_id: int):
        return await self._repository.get_message(chat_id, message_id, user_id)

    async def get_chat_history(
        self, chat_id: int, user_id: int, limit: int = 10, message_id: int = None
    ):
        return await self._repository.get_chat_history(
            chat_id, user_id, limit, message_id
        )
