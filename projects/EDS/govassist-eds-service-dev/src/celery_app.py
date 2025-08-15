import ssl

from celery import Celery
from kombu import Queue
from redis import ConnectionError, Redis, TimeoutError
from socketio import AsyncRedisManager

from src.core.config import configs
from src.core.database import Database
from src.socket_io.server import SocketIOService

# Configure once, reuse everywhere
redis_client: Redis = Redis.from_url(
    configs.REDIS_URL,
    socket_timeout=30.0,  # Increased socket timeout
    socket_connect_timeout=10.0,  # Connection timeout
    socket_keepalive=True,  # Enable keepalive
    socket_keepalive_options={},  # Keepalive options
    retry_on_timeout=True,  # Retry on timeout
    retry_on_error=[TimeoutError, ConnectionError],  # Retry on specific errors
    health_check_interval=30,  # Health check interval
    max_connections=configs.REDIS_MAX_CONNECTIONS,  # Use config max connections
)
socket_io_service = SocketIOService(client_manager=AsyncRedisManager(configs.REDIS_URL))

# Use the existing Database class instead of creating duplicate engine
database = Database(configs.DATABASE_URI)

# Initialize Celery
celery_app = Celery(
    "govt_assist_eds",
    broker=configs.BROKER_URL,
    backend=None,
)

# Basic Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task settings
    task_track_started=True,
    task_time_limit=86400,  # 24 hours
    task_acks_late=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    # # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Results
    result_expires=3600,  # 1 hour
    # Queue
    task_default_queue="eds_default_queue_dev",
    task_queues=(
        Queue("eds_default_queue_dev"),
        Queue("eds_excel_ingestion_queue_dev"),
        Queue("eds_report_migration_queue_dev"),
    ),
    task_routes={
        "src.tasks.sharepoint_webhook_handler": {"queue": "eds_excel_ingestion_queue_dev"},
        "src.tasks.sub_report_tasks": {"queue": "eds_report_migration_queue_dev"},
    },
    broker_transport_options={
        "visibility_timeout": 3600,
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(
    [
        "src.tasks.sharepoint_webhook_handler",
        "src.tasks.sub_report_tasks",
        "src.tasks.report_export",
    ]
)

# Simple retry configuration
celery_app.conf.task_annotations = {
    "*": {
        "max_retries": 3,
        "default_retry_delay": 60,
    },
}
