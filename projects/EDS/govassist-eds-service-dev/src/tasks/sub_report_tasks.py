from celery.exceptions import MaxRetriesExceededError
from loguru import logger

from src.celery_app import celery_app
from src.core.container import Container
from src.services.sub_report_service import SubReportService


@celery_app.task(
    queue="eds_report_migration_queue_dev",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def migrate_sub_report_data(self, sub_report_id: int):
    """
    Celery task to migrate sub-report data from SQL to Elasticsearch
    """
    try:
        service = SubReportService(Container.session_factory())
        success = service._migrate_data(sub_report_id)
        if success:
            logger.info(
                f"Migration completed successfully for sub_report_id: {sub_report_id}"
            )
        else:
            logger.error(f"Migration failed for sub_report_id: {sub_report_id}")
        return success
    except Exception as e:
        logger.error(f"Migration task failed for sub_report_id {sub_report_id}: {e}")

        # Retry the task if we haven't exceeded max retries
        try:
            self.retry(countdown=60, max_retries=3)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for sub_report_id {sub_report_id}")
            raise
