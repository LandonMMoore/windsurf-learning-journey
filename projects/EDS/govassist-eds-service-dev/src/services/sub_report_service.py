import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Tuple

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from src.agents.tools.es_tools import es_client
from src.celery_app import redis_client
from src.core.exceptions import NotFoundError, ValidationError
from src.model.report_model import ReportConfiguration
from src.model.sub_report_model import SubReport, SubReportWorkflow
from src.repository.sub_report_repository import SubReportRepository
from src.schema.report_schema import (
    LARK_PARSER,
    FormulaFieldValidator,
    SubReportConfigBaseSchema,
)
from src.services.base_service import BaseService
from src.util.project_detail import convert_to_dict
from src.util.reports import (
    build_filter_condition,
    build_sqlalchemy_query,
    make_report_redis_key,
    resolve_join_chain,
)

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def get_es_mapping(sql_type: str) -> Dict[str, Any]:
    mapping_map = {
        "int": {"type": "scaled_float", "scaling_factor": 100000},
        "integer": {"type": "scaled_float", "scaling_factor": 100000},
        "float": {"type": "scaled_float", "scaling_factor": 100000},
        "double": {"type": "scaled_float", "scaling_factor": 100000},
        "decimal": {"type": "scaled_float", "scaling_factor": 100000},
        "date": {"type": "date"},
        "datetime": {"type": "date"},
        "timestamp": {"type": "date"},
        "boolean": {"type": "boolean"},
        "str": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "string": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "text": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "varchar": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "char": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
    }
    return mapping_map.get(
        sql_type.lower(), {"type": "text", "fields": {"keyword": {"type": "keyword"}}}
    )


class SubReportService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(SubReportRepository(session_factory))
        self.batch_size = 500

    def _create_index_with_mapping(
        self, index_name: str, field_types_dict: Dict[str, str]
    ) -> str:
        """Create Elasticsearch index with appropriate mapping from SQL types."""

        properties = {
            col: get_es_mapping(py_type) for col, py_type in field_types_dict.items()
        }
        body = {"mappings": {"properties": properties}}

        try:
            if es_client.indices.exists(index=index_name):
                es_client.indices.delete(index=index_name)

            es_client.indices.create(index=index_name, body=body)
            return index_name
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            raise

    def _get_total_count_from_query(self, session: Session, count_query: str) -> int:
        """Get total count using the existing count query"""
        try:
            result = session.execute(text(count_query))
            count = result.scalar()
            result.close()
            return count
        except Exception:
            logger.error("Error getting total count from query")
            raise

    def _update_workflow_status(
        self,
        session: Session,
        workflow_id: int,
        status: WorkflowStatus,
        log_entry: str = None,
    ) -> None:
        update_fields = {
            "status": status.value,
        }

        if status == WorkflowStatus.COMPLETED:
            update_fields["execution_success_time"] = datetime.now(timezone.utc)

        if log_entry:
            update_fields["error_log"] = log_entry

        rows_updated = (
            session.query(SubReportWorkflow)
            .filter_by(id=workflow_id)
            .update(update_fields, synchronize_session=False)
        )

        session.commit()

        if rows_updated:
            logger.debug(f"Workflow {workflow_id} status updated to '{status.value}'")
        else:
            logger.warning(f"No workflow found with ID {workflow_id} — update skipped")

    def _process_batch(
        self,
        session: Session,
        query: str,
        index_name: str,
        batch_number: int,
        offset: int,
    ) -> bool:
        """Process a single batch of data"""
        try:
            paginated_query = (
                f"{query} OFFSET {offset} ROWS FETCH NEXT {self.batch_size} ROWS ONLY"
            )
            result = session.execute(text(paginated_query))
            columns = [col[0] for col in result.cursor.description]
            rows = result.fetchall()
            result.close()

            if not rows:
                return True

            self._bulk_insert_to_elasticsearch(index_name, rows, columns, batch_number)
            return True

        except Exception as e:
            logger.error(f"Batch {batch_number} failed: {e}")
            return False

    def _bulk_insert_to_elasticsearch(
        self, index_name: str, rows: List[tuple], columns: List[str], batch_number: int
    ) -> None:
        """Insert documents to Elasticsearch using bulk API (optimized)"""

        def generate_bulk_payload():
            for row in rows:
                doc = {}
                for col, val in zip(columns, row):
                    if isinstance(val, datetime):
                        doc[col] = val.isoformat()
                    else:
                        doc[col] = val
                yield {"index": {"_index": index_name}}
                yield doc

        try:
            es_client.bulk(body=generate_bulk_payload(), request_timeout=300)
            logger.debug(
                f"Batch {batch_number}: Successfully inserted {len(rows)} documents to Elasticsearch"
            )
        except Exception as e:
            logger.debug(f"Batch {batch_number}: Elasticsearch bulk insert failed: {e}")
            raise

    def _migrate_data(self, sub_report_id: int) -> bool:
        """Migrate data from SQL to Elasticsearch in batches without retry"""
        with self._repository.session_factory() as session:
            try:
                # Get sub_report to get index_name
                sub_report = (
                    session.query(SubReport).filter_by(id=sub_report_id).first()
                )
                if not sub_report:
                    logger.debug(f"Sub-report {sub_report_id} not found")
                    return False

                workflow = (
                    session.query(SubReportWorkflow)
                    .filter_by(sub_report_id=sub_report_id)
                    .order_by(SubReportWorkflow.id.desc())
                    .first()
                )

                if not workflow:
                    logger.error(
                        f"No workflow found for sub_report_id: {sub_report_id}"
                    )
                    return False

                redis_key = make_report_redis_key(
                    sub_report.report_configuration_id, sub_report_id, sub_report.config
                )
                cached_result = redis_client.get(redis_key)
                if cached_result is not None and isinstance(cached_result, bytes):
                    cached_result = json.loads(cached_result.decode("utf-8"))

                if (
                    cached_result is not None
                    and isinstance(cached_result, dict)
                    and "db_query" in cached_result
                    and "count_query" in cached_result
                    and "field_types" in cached_result
                ):
                    db_query = cached_result["db_query"]
                    count_query = cached_result["count_query"]
                    field_types = cached_result["field_types"]
                else:
                    db_query, count_query, field_types = (
                        self._build_query_and_extract_field_types(session, sub_report)
                    )

                self._create_index_with_mapping(sub_report.index_name, field_types)

                # Start workflow
                self._update_workflow_status(
                    session, workflow.id, WorkflowStatus.IN_PROGRESS
                )

                # Use existing count query from db_query
                total_count = self._get_total_count_from_query(session, count_query)
                if total_count == 0:
                    self._update_workflow_status(
                        session,
                        workflow.id,
                        WorkflowStatus.COMPLETED,
                        log_entry="No records to migrate",
                    )
                    return True

                total_batches = (total_count + self.batch_size - 1) // self.batch_size
                logger.debug(
                    f"Starting migration: {total_count} total records, {total_batches} batches of {self.batch_size}"
                )

                error_log = None
                status = None
                for batch_number in range(1, total_batches + 1):
                    offset = (batch_number - 1) * self.batch_size
                    logger.debug(
                        f"Processing batch {batch_number}/{total_batches} (offset: {offset})"
                    )

                    success = self._process_batch(
                        session,
                        db_query,
                        sub_report.index_name,
                        batch_number,
                        offset,
                    )
                    if not success:
                        error_log = f"Batch {batch_number} failed"
                        status = WorkflowStatus.FAILED
                        break
                    else:
                        logger.debug(
                            f"Batch {batch_number}/{total_batches} completed successfully"
                        )
                else:
                    status = WorkflowStatus.COMPLETED

            except Exception as e:
                logger.error(f"Migration failed for sub_report_id: {sub_report_id}")
                status = WorkflowStatus.FAILED
                error_log = f"Migration error: {str(e)}"

            finally:
                self._update_workflow_status(
                    session,
                    workflow.id,
                    status,
                    log_entry=error_log,
                )
                return status == WorkflowStatus.COMPLETED

    def publish_sub_report(self, sub_report_id: int) -> Dict[str, Any]:
        from src.tasks.sub_report_tasks import migrate_sub_report_data

        with self._repository.session_factory() as session:
            try:
                sub_report = session.get(SubReport, sub_report_id)
                if not sub_report:
                    raise NotFoundError(
                        detail=f"Sub-report with ID {sub_report_id} was not found."
                    )

                # Check if migration is already in progress
                workflow = (
                    session.query(SubReportWorkflow)
                    .filter(
                        SubReportWorkflow.sub_report_id == sub_report_id,
                        SubReportWorkflow.status.in_(
                            [
                                WorkflowStatus.IN_PROGRESS.value,
                                WorkflowStatus.PENDING.value,
                            ]
                        ),
                    )
                    .order_by(SubReportWorkflow.id.desc())
                    .first()
                )

                if workflow:
                    return {"message": "Sub-report migration is already in progress"}

                workflow = self._create_workflow_record(session, sub_report_id)
                migrate_sub_report_data.delay(sub_report_id)

                return {"message": "Sub-report migration started successfully"}

            except Exception as e:
                logger.error(f"Error publishing sub-report: {e}")
                session.rollback()
                raise

    def _create_workflow_record(
        self, session: Session, sub_report_id: int
    ) -> SubReportWorkflow:
        """Create a new workflow record"""
        workflow = SubReportWorkflow(
            sub_report_id=sub_report_id, status=WorkflowStatus.PENDING.value
        )
        session.add(workflow)
        session.commit()
        return workflow

    def _build_query_and_extract_field_types(
        self, session: Session, sub_report: SubReport
    ) -> Tuple[str, str, Dict[str, str]]:
        """Build SQLAlchemy query and extract field types from sub_report config"""
        try:
            # Validate the sub_report config
            sub_report_config = sub_report.config
            if not sub_report_config:
                raise ValidationError(detail="Sub report config not present.")

            SubReportConfigBaseSchema.model_validate(sub_report_config)

            # Build the SQLAlchemy query similar to reports service
            filters = sub_report_config["filters"]
            base, join_plan = resolve_join_chain(
                sub_report_config["config"], sub_report_config.get("group_by", [])
            )
            stmt, count_stmt, data_type_map, formula_map = build_sqlalchemy_query(
                session, sub_report_config, base, join_plan
            )

            # Apply filters if they exist
            if filters:
                filter_expr = build_filter_condition(
                    filters, data_type_map, formula_map
                )
                if filter_expr is not None:
                    stmt = stmt.where(filter_expr)
                    count_stmt = count_stmt.where(filter_expr)

            # Compile the queries to strings
            db_query = str(stmt.compile(compile_kwargs={"literal_binds": True}))
            count_query = f"SELECT COUNT(*) FROM ({count_stmt.compile(compile_kwargs={'literal_binds': True})}) AS subquery"

            return db_query, count_query, data_type_map

        except Exception:
            logger.error("Error building query and extracting field types")
            raise ValidationError(detail="Error building query")

    def validate_formula(self, formula: str) -> dict:
        try:
            tree = LARK_PARSER.parse(formula)

            visitor = FormulaFieldValidator()
            visitor.visit(tree)

            return {
                "message": "Formula is valid",
            }
        except Exception as e:
            raise ValidationError(detail=str(e))

    def get_sub_report_workflow_details(
        self, report_configuration_id: int
    ) -> List[Dict[str, Any]]:
        with self._repository.session_factory() as session:
            if (
                not session.query(ReportConfiguration)
                .filter_by(id=report_configuration_id)
                .first()
            ):
                raise NotFoundError(
                    detail=f"Report configuration with ID {report_configuration_id} not found"
                )

            latest_workflow_ids = (
                session.query(
                    SubReportWorkflow.sub_report_id,
                    func.max(SubReportWorkflow.id).label("max_id"),
                )
                .join(SubReport, SubReportWorkflow.sub_report_id == SubReport.id)
                .filter(SubReport.report_configuration_id == report_configuration_id)
                .group_by(SubReportWorkflow.sub_report_id)
                .subquery()
            )

            latest_workflows = (
                session.query(SubReportWorkflow)
                .join(
                    latest_workflow_ids,
                    SubReportWorkflow.sub_report_id
                    == latest_workflow_ids.c.sub_report_id,
                )
                .filter(SubReportWorkflow.id == latest_workflow_ids.c.max_id)
                .all()
            )

            return [convert_to_dict(workflow) for workflow in latest_workflows]
