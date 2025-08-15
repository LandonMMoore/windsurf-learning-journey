import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from loguru import logger

from src.celery_app import celery_app, database, redis_client
from src.core.workflow_handler import CeleryWorkflowManager
from src.model.workflow import EdsWorkflowProgress
from src.repository.workflow_repository import WorkflowRepository
from src.schema.workflow_schema import (
    LogLevel,
    WorkflowProgressCreate,
    WorkflowStateUpdate,
    WorkflowStatus,
    WorkflowStatusEnum,
    WorkflowStepEnum,
    WorkflowUpdate,
)
from src.services.workflow_crud_service import WorkflowCrudService
from src.services.workflow_redis_manager import WorkflowRedisSchema
from src.services.workflow_service import ExcelDataMigrationService, MigrationResult


@celery_app.task(
    queue="eds_excel_ingestion_queue_dev",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def process_sharepoint_workflow(
    self, workflow_id: str, processable_items: List[Dict[str, Any]], workflow_db_id: int
):
    logger.info(f"Processing SharePoint workflow: {workflow_id}")
    downloaded_files = []
    validated_sheets_data = []
    workflow_manager = CeleryWorkflowManager(
        redis_client=redis_client,
        schema=WorkflowRedisSchema(),
        workflow_service=WorkflowCrudService(session_factory=database.session),
    )
    try:
        # Update the workflow status to running
        workflow_obj = workflow_manager.workflow_service.get_by_id(id=workflow_db_id)
        updated_workflow = WorkflowUpdate(
            status=WorkflowStatusEnum.RUNNING,
            workflow_started_at=datetime.now(timezone.utc),
            total_files=len(processable_items),
        )
        workflow_manager.workflow_service.patch(workflow_obj.id, updated_workflow)

        downloaded_files, files_failed, scaled_progres = (
            workflow_manager.download_sharepoint_files(
                workflow_id, processable_items, workflow_db_id
            )
        )

        updated_workflow = WorkflowUpdate(
            progress_percentage=scaled_progres, files_failed=files_failed
        )
        workflow_manager.workflow_service.patch(workflow_obj.id, updated_workflow)

        valid_files, files_failed, scaled_progres = workflow_manager.validate_downloaded_files(
            workflow_id, downloaded_files, workflow_db_id
        )
        validated_sheets_data = workflow_manager.validate_sheets_data(valid_files)

        updated_workflow = WorkflowUpdate(
            progress_percentage=scaled_progres, files_failed=files_failed
        )
        workflow_manager.workflow_service.patch(workflow_obj.id, updated_workflow)

        processed_results, files_failed, scaled_progres = (
            workflow_manager.process_valid_files(
                workflow_id, validated_sheets_data, workflow_db_id
            )
        )

        workflow_manager.add_log_sync(
            workflow_id,
            workflow_db_id,
            LogLevel.INFO,
            "Workflow completed successfully",
            step=WorkflowStepEnum.COMPLETION.value,
        )

        updated_workflow = WorkflowUpdate(
            progress_percentage=scaled_progres,
            files_processed=len(processed_results),
            files_failed=files_failed,
            status=WorkflowStatusEnum.COMPLETED,
            workflow_completed_at=datetime.now(timezone.utc),
        )

        workflow_logs_key = workflow_manager.schema.workflow_logs_key(workflow_id)
        workflow_progress_logs = list(
            reversed(workflow_manager.redis_client.lrange(workflow_logs_key, 0, -1))
        )

        workflow_progress_orm = [
            EdsWorkflowProgress(
                **WorkflowProgressCreate(**json.loads(log.decode("utf-8"))).model_dump(
                    exclude={"level"}, exclude_unset=True
                )
            )
            for log in workflow_progress_logs
        ]

        workflow_manager.workflow_service.bulk_add_workflow_progress(
            workflow_progress_orm
        )

        workflow_manager.workflow_service.patch(workflow_obj.id, updated_workflow)
        # Clear the workflow status
        workflow_manager.clear_workflow_status(workflow_id)
        workflow_manager.clear_workflow_state(workflow_id)
        workflow_manager.clear_workflow_logs(workflow_id)

        return {
            "status": "completed",
            "processed_files": len(processed_results),
            "total_files": len(processable_items),
        }

    except Exception as e:
        logger.error(f"Workflow failed for {workflow_id}: {str(e)}")
        try:
            workflow_manager.add_log_sync(
                workflow_id,
                workflow_db_id,
                LogLevel.ERROR,
                f"Workflow failed: {str(e)}",
                step=WorkflowStepEnum.ERROR.value,
            )
            workflow_manager.update_workflow_status_sync(
                workflow_id,
                WorkflowStateUpdate(
                    status=WorkflowStatus.FAILED.value,
                    files_failed=len(processable_items),
                    completed_at=datetime.now(timezone.utc).isoformat(),
                ),
            )
        except Exception as log_error:
            logger.error(f"Failed to log workflow error: {log_error}")

        # Retry the task if we haven't exceeded max retries
        try:
            self.retry(countdown=60, max_retries=3)
        except Exception as retry_error:
            logger.error(
                f"Max retries exceeded for workflow {workflow_id}: {retry_error}"
            )
            raise
    finally:
        # Delete the file manually
        if downloaded_files:
            for file in downloaded_files:
                if os.path.exists(file["content"]):
                    os.remove(file["content"])
                    logger.info("Temporary valid file deleted.")

        if validated_sheets_data:
            for file in validated_sheets_data:
                if os.path.exists(file["file_path_of_invalid_data"]):
                    os.remove(file["file_path_of_invalid_data"])
                    logger.info("Temporary invalid file deleted.")