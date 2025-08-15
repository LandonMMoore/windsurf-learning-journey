import json
import logging
import tempfile
from datetime import UTC
from datetime import datetime as dt

from openpyxl import Workbook
from sqlalchemy import text

from src.agents.tools.es_tools import es_client
from src.celery_app import celery_app, database, redis_client
from src.core.config import configs
from src.core.extensions import blob_service_client
from src.model.report_model import ReportExport
from src.model.sub_report_model import SubReportWorkflow
from src.services.sub_report_service import SubReportService
from src.util.reports import make_report_redis_key

logger = logging.getLogger(__name__)


def upload_file_to_blob(file_path: str, container_name: str, blob_name: str) -> str:
    """
    Uploads a local file to Azure Blob Storage and returns the blob URL.
    """
    # Ensure container exists (optional)
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception:
        pass  # already exists

    blob_client = container_client.get_blob_client(blob=blob_name)

    # Upload file
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


def feed_sheet_from_db(ws, session, sub_report, service):
    redis_key = make_report_redis_key(
        sub_report.report_configuration_id,
        sub_report.id,
        sub_report.config,
    )
    cached_result = redis_client.get(redis_key)
    cached = json.loads(cached_result.decode("utf-8")) if cached_result else {}
    db_query = cached.get("db_query")
    count_query = cached.get("count_query")

    if not db_query or not count_query:
        db_query, count_query, _ = service._build_query_and_extract_field_types(
            session, sub_report
        )

    total = service._get_total_count_from_query(session, count_query)
    if total == 0:
        logger.warning(f"No records found for sub-report: {sub_report.name}")
        return

    batch_size = 1000
    offset = 0

    while offset < total:
        query = f"{db_query} OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY"
        result = session.execute(text(query))
        rows = result.fetchall()

        for row in rows:
            ws.append(list(row))

        offset += batch_size


def feed_sheet_from_es(ws, sub_report, fields_by_uuid):
    batch_size = 1000
    search_after = None

    while True:
        query = {
            "size": batch_size,
            "query": {"match_all": {}},
            "sort": [{"_doc": "asc"}],
            "_source": True,
        }
        if search_after:
            query["search_after"] = search_after

        response = es_client.search(index=sub_report.index_name, body=query)
        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            break

        for hit in hits:
            source = hit.get("_source", {})
            row = [source.get(f, "") for f in fields_by_uuid if f in source]
            ws.append(row)

        search_after = hits[-1]["sort"]


@celery_app.task(
    queue="eds_default_queue_dev",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def report_export(self, export_id: int):
    with database.session() as session:
        export = (
            session.query(ReportExport).filter(ReportExport.id == export_id).first()
        )
        if not export:
            logger.error(f"Export not found for id: {export_id}")
            return

        if export.status in ["COMPLETED", "FAILED", "IN_PROGRESS"]:
            logger.warning(
                f"Export already {export.status} for id: {export_id}, skipping."
            )
            return

        def fail_export(message: str):
            export.status = "FAILED"
            export.error_message = message
            session.commit()
            logger.error(message)

        try:
            export.status = "IN_PROGRESS"
            session.commit()
            session.refresh(export)

            report = export.report
            sub_reports = report.sub_reports

            if not sub_reports:
                return fail_export("No sub-reports found for report")

            file_name = (
                f"{report.name}_{dt.now(UTC).strftime('%Y-%m-%dT%H-%M-%S')}.xlsx"
            )
            workbook = Workbook()
            workbook.remove(workbook.active)

            service = SubReportService(session)

            for sub_report in sub_reports:
                sheet_name = sub_report.name[:31]
                ws = workbook.create_sheet(title=sheet_name)
                latest_workflow = (
                    session.query(SubReportWorkflow)
                    .filter(SubReportWorkflow.sub_report_id == sub_report.id)
                    .order_by(SubReportWorkflow.id.desc())
                    .first()
                )

                fields_by_uuid = {c["uuid"]: c for c in sub_report.config["config"]}
                headers = [fields_by_uuid[f]["label"] for f in fields_by_uuid]
                ws.append(headers)

                if (
                    not latest_workflow
                    or latest_workflow.status != "COMPLETED"
                    or not es_client.indices.exists(index=sub_report.index_name)
                ):
                    # If the report is not published to the elasticsearch, we will have to pull the data from the sql.
                    feed_sheet_from_db(ws, session, sub_report, service)
                else:
                    # If the report is published to the elasticsearch, we will have to pull the data from the elasticsearch.
                    feed_sheet_from_es(ws, sub_report, fields_by_uuid)

            with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
                workbook.save(tmp.name)
                blob_name = f"report-{file_name}"
                container = configs.AZURE_STORAGE_CONTAINER_NAME
                upload_file_to_blob(tmp.name, container, blob_name)

            export.status = "COMPLETED"
            export.file_name = blob_name
            session.commit()
            logger.info(f"Export successful for report {report.name}")

        except Exception as e:
            fail_export(str(e))
            logger.exception(f"Export task failed for report_id {export_id}")
