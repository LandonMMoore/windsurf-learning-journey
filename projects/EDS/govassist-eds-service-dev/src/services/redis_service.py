import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from loguru import logger

from src.core.config import configs
from src.core.redis_client import RedisClient
from src.core.redis_config import SerializationMethod
from src.schema.workflow_schema import (
    FileProcessingInfo,
    FileProcessingStatus,
    FolderType,
    LogLevel,
    WorkflowLogEntry,
    WorkflowState,
    WorkflowStepEnum,
)
from src.services.workflow_redis_manager import WorkflowRedisSchema


class WorkflowKeyBuilder:
    """Handles workflow-specific key generation"""

    @staticmethod
    def build_key(workflow_id: str, *parts: str, prefix: str = "workflow") -> str:
        """Build workflow key with consistent naming"""
        return f"{prefix}:{workflow_id}:" + ":".join(parts)

    @staticmethod
    def session_key(session_id: str) -> str:
        """Build session key"""
        return f"session:{session_id}"

    @staticmethod
    def lock_key(resource: str) -> str:
        """Build lock key"""
        return f"lock:{resource}"


class SessionManager:
    """Manages session operations"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.key_builder = WorkflowKeyBuilder()

    async def set_session(
        self, session_id: str, session_data: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """Set session data"""
        key = self.key_builder.session_key(session_id)
        return await self.redis_client.set(
            key, session_data, ttl, serialization=SerializationMethod.JSON
        )

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        key = self.key_builder.session_key(session_id)
        return await self.redis_client.get(key, serialization=SerializationMethod.JSON)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        key = self.key_builder.session_key(session_id)
        return await self.redis_client.delete(key) > 0


class LockManager:
    """Manages distributed locking"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.key_builder = WorkflowKeyBuilder()

    async def acquire_lock(self, resource: str, timeout: float = 10.0) -> bool:
        """Acquire distributed lock"""
        key = self.key_builder.lock_key(resource)
        return await self.redis_client.acquire_lock(key, timeout)

    async def release_lock(self, resource: str) -> bool:
        """Release distributed lock"""
        key = self.key_builder.lock_key(resource)
        return await self.redis_client.release_lock(key)


class CacheManager:
    """Manages general cache operations"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value"""
        try:
            return await self.redis_client.set(
                key, value, ttl, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[CacheManager][set] Failed for key={key}: {e}")
            return False

    async def get(self, key: str) -> Any:
        """Get cache value"""
        try:
            return await self.redis_client.get(
                key, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[CacheManager][get] Failed for key={key}: {e}")
            return None

    async def delete(self, *keys: str) -> int:
        """Delete cache keys"""
        try:
            return await self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"[CacheManager][delete] Failed: {e}")
            return 0


class HashManager:
    """Manages hash operations"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def set(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set hash mapping"""
        try:
            await self.redis_client.hset(
                key, mapping=mapping, serialization=SerializationMethod.JSON
            )
            return True
        except Exception as e:
            logger.error(f"[HashManager][set] Failed for key={key}: {e}")
            return False

    async def get(self, key: str, field: str) -> Optional[str]:
        """Get hash field"""
        try:
            return await self.redis_client.hget(
                key, field, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[HashManager][get] Failed for key={key}, field={field}: {e}")
            return None

    async def get_all(self, key: str) -> Dict[str, Any]:
        """Get all hash fields"""
        try:
            return await self.redis_client.hgetall(
                key, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[HashManager][get_all] Failed for key={key}: {e}")
            return {}


class SetManager:
    """Manages set operations"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def add(self, key: str, *values: Any) -> int:
        """Add values to set"""
        try:
            return await self.redis_client.sadd(
                key, *values, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[SetManager][add] Failed for key={key}: {e}")
            return 0

    async def members(self, key: str) -> List[str]:
        """Get set members"""
        try:
            return await self.redis_client.smembers(
                key, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[SetManager][members] Failed for key={key}: {e}")
            return []


class ListManager:
    """Manages list operations"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to left of list"""
        try:
            return await self.redis_client.lpush(
                key, *values, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[ListManager][lpush] Failed for key={key}: {e}")
            return 0

    async def rpush(self, key: str, *values: Any) -> int:
        """Push values to right of list"""
        try:
            return await self.redis_client.rpush(
                key, *values, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[ListManager][rpush] Failed for key={key}: {e}")
            return 0

    async def range(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get range of list elements"""
        try:
            return await self.redis_client.lrange(
                key, start, end, serialization=SerializationMethod.JSON
            )
        except Exception as e:
            logger.error(f"[ListManager][range] Failed for key={key}: {e}")
            return []


class KeyManager:
    """Manages key operations"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def find(self, pattern: str) -> List[str]:
        """Find keys matching pattern"""
        try:
            return await self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"[KeyManager][find] Failed for pattern={pattern}: {e}")
            return []

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on key"""
        try:
            return await self.redis_client.expire(key, ttl)
        except Exception as e:
            logger.error(f"[KeyManager][expire] Failed for key={key}: {e}")
            return False


class WorkflowManager:
    """Manages workflow state in Redis using RedisService"""

    def __init__(self, redis_service: "RedisService"):
        self.redis_service = redis_service
        self.schema = WorkflowRedisSchema()

    async def create_workflow(
        self,
        drive_id: str,
        folder_id: str,
        folder_name: str,
        folder_type: FolderType,
        processable_items: List[Dict[str, Any]],
        db_workflow_id: int,
    ) -> str:
        workflow_id = folder_id
        files = {}
        for item in processable_items:
            file_id = item.get("id", str(uuid.uuid4()))
            file_info = FileProcessingInfo(
                file_id=file_id,
                file_name=item.get("name", "unknown"),
                download_url=item.get("@microsoft.graph.downloadUrl", ""),
            )
            files[file_id] = file_info
        workflow = WorkflowState(
            workflow_id=workflow_id,
            drive_id=drive_id,
            folder_id=folder_id,
            folder_name=folder_name,
            folder_type=folder_type,
            total_files=len(processable_items),
            files=files,
        )
        # Store in Redis as JSON string
        await self.redis_service.cache_set(
            self.schema.workflow_state_key(workflow_id),
            workflow.model_dump(),
            86400 * 7,
        )
        # emit workflow update to workflow updates channel
        await self.emit_workflow_update_async(
            workflow_id, "created", workflow.model_dump()
        )
        # Set expiry for logs list
        await self.redis_service.expire(
            self.schema.workflow_logs_key(workflow_id), 86400 * 7
        )
        await self.add_log(
            workflow_id,
            db_workflow_id,
            LogLevel.INFO,
            "Workflow created",
            step=WorkflowStepEnum.INITIALIZATION.value,
        )
        logger.info("Workflow created")
        return workflow_id

    async def update_file_status(
        self,
        workflow_id: str,
        workflow_db_id: int,
        file_id: str,
        status: FileProcessingStatus,
        progress: Optional[float] = None,
        validation_errors: Optional[List[str]] = None,
        validation_warnings: Optional[List[str]] = None,
        row_counts: Optional[Dict[str, int]] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow or file_id not in workflow.files:
                return False
            file_info = workflow.files[file_id]
            file_info.status = status
            if progress is not None:
                file_info.progress_percentage = min(100.0, max(0.0, progress))
            if validation_errors:
                file_info.validation_errors.extend(validation_errors)
            if validation_warnings:
                file_info.validation_warnings.extend(validation_warnings)
            if row_counts:
                file_info.valid_rows_count = row_counts.get("valid", 0)
                file_info.invalid_rows_count = row_counts.get("invalid", 0)
                file_info.total_rows = row_counts.get("total", 0)
            if error_message:
                file_info.error_message = error_message
            if status in [FileProcessingStatus.PROCESSED, FileProcessingStatus.FAILED]:
                file_info.processed_at = datetime.now(timezone.utc)
            workflow.files_processed = sum(
                1
                for f in workflow.files.values()
                if f.status
                in [FileProcessingStatus.PROCESSED, FileProcessingStatus.FAILED]
            )
            workflow.files_failed = sum(
                1
                for f in workflow.files.values()
                if f.status == FileProcessingStatus.FAILED
            )
            if workflow.total_files > 0:
                workflow.progress_percentage = (
                    workflow.files_processed / workflow.total_files
                ) * 100
            await self.redis_service.cache_set(
                self.schema.workflow_state_key(workflow_id),
                workflow.model_dump(),
                86400 * 7,
            )
            await self.add_log(
                workflow_id,
                workflow_db_id,
                LogLevel.INFO,
                f"File {file_info.file_name} status updated to {status.value}",
                file_name=file_info.file_name,
                step=WorkflowStepEnum.PROCESSING.value,
                details={"progress": progress, "error": error_message},
            )
            return True
        except Exception:
            logger.error("Failed to update file")
            return False

    async def add_log(
        self,
        workflow_id: str,
        workflow_db_id: int,
        level: LogLevel,
        message: str,
        file_name: Optional[str] = None,
        step: Optional[str] = None,
    ):
        """Synchronous log addition for Celery tasks"""
        log_entry = {
            "workflow_id": workflow_db_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.value,
            "message": message,
            "file_name": file_name,
            "step": step,
        }
        await self.redis_service.list_lpush(
            self.schema.workflow_logs_key(workflow_id), log_entry
        )

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        try:
            data = await self.redis_service.cache_get(
                self.schema.workflow_state_key(workflow_id)
            )
            if data:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                if isinstance(data, str):
                    data = json.loads(data)
                return WorkflowState.model_validate(data)
            return None
        except Exception:
            logger.error("Failed to get workflow")
            return None

    async def get_workflow_logs(
        self, workflow_id: str, limit: int = 100, offset: int = 0
    ) -> List[WorkflowLogEntry]:
        try:
            logs_data = await self.redis_service.list_range(
                self.schema.workflow_logs_key(workflow_id), offset, offset + limit - 1
            )
            logs = []
            for log_data in logs_data:
                try:
                    logs.append(WorkflowLogEntry.model_validate_json(log_data))
                except Exception:
                    continue  # Skip malformed logs
            return logs
        except Exception:
            logger.error("Failed to get logs for workflow")
            return []

    async def register_task(self, workflow_id: str, task_id: str):
        workflow = await self.get_workflow(workflow_id)
        if workflow:
            workflow.task_id = task_id
            await self.redis_service.cache_set(
                self.schema.workflow_state_key(workflow_id),
                workflow.model_dump(),
                86400 * 7,
            )

    async def emit_workflow_update_async(
        self, workflow_id: str, status: str, workflow_data: Dict[str, Any]
    ):
        """Emit workflow update via Redis Pub/Sub (Celery pushes to Redis, server emits via Socket.IO)"""
        try:
            # Create the message to publish to Redis
            message = {
                "workflow_id": workflow_id,
                "status": status,
                "data": workflow_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Publish to Redis channel (synchronous operation)
            await self.redis_service.pubsub.publish(
                configs.WORKFLOW_UPDATES, json.dumps(message)
            )

        except Exception as e:
            logger.error(f"Failed to publish workflow update to Redis: {e}")


class PubSubManager:
    """Manages Redis Pub/Sub operations"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def publish(self, channel: str, message: str):
        await self.redis_client.publish(channel, message)

    async def subscribe(self, channel: str):
        await self.redis_client.subscribe(channel)


class RedisService:
    """Mature, simple Redis service with modular design"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

        # Initialize managers
        self.workflow = WorkflowManager(self)
        self.session = SessionManager(redis_client)
        self.lock = LockManager(redis_client)
        self.cache = CacheManager(redis_client)
        self.hash = HashManager(redis_client)
        self.set = SetManager(redis_client)
        self.list = ListManager(redis_client)
        self.key = KeyManager(redis_client)
        self.pubsub = PubSubManager(redis_client)

        # Advanced workflow manager (schema-driven, index-aware)
        # self.advanced_workflow = AdvancedWorkflowManager(redis_client) # This line is removed as per the edit hint

    # Convenience methods for backward compatibility
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value (alias for cache.set)"""
        return await self.cache.set(key, value, ttl)

    async def cache_get(self, key: str) -> Any:
        """Get cache value (alias for cache.get)"""
        return await self.cache.get(key)

    async def cache_delete(self, *keys: str) -> int:
        """Delete cache keys (alias for cache.delete)"""
        return await self.cache.delete(*keys)

    async def set_session(
        self, session_id: str, session_data: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """Set session (alias for session.set_session)"""
        return await self.session.set_session(session_id, session_data, ttl)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session (alias for session.get_session)"""
        return await self.session.get_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session (alias for session.delete_session)"""
        return await self.session.delete_session(session_id)

    async def acquire_lock(self, resource: str, timeout: float = 10.0) -> bool:
        """Acquire lock (alias for lock.acquire_lock)"""
        return await self.lock.acquire_lock(resource, timeout)

    async def release_lock(self, resource: str) -> bool:
        """Release lock (alias for lock.release_lock)"""
        return await self.lock.release_lock(resource)

    # Hash convenience methods
    async def hash_set(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set hash (alias for hash.set)"""
        return await self.hash.set(key, mapping)

    async def hash_get(self, key: str, field: str) -> Optional[str]:
        """Get hash field (alias for hash.get)"""
        return await self.hash.get(key, field)

    async def hash_getall(self, key: str) -> Dict[str, Any]:
        """Get all hash fields (alias for hash.get_all)"""
        return await self.hash.get_all(key)

    # Set convenience methods
    async def set_add(self, key: str, *values: Any) -> int:
        """Add to set (alias for set.add)"""
        return await self.set.add(key, *values)

    async def set_members(self, key: str) -> List[str]:
        """Get set members (alias for set.members)"""
        return await self.set.members(key)

    # List convenience methods
    async def list_lpush(self, key: str, *values: Any) -> int:
        """Left push (alias for list.lpush)"""
        return await self.list.lpush(key, *values)

    async def list_rpush(self, key: str, *values: Any) -> int:
        """Right push (alias for list.rpush)"""
        return await self.list.rpush(key, *values)

    async def list_range(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get range (alias for list.range)"""
        return await self.list.range(key, start, end)

    # Key convenience methods
    async def keys(self, pattern: str) -> List[str]:
        """Find keys (alias for key.find)"""
        return await self.key.find(pattern)

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL (alias for key.expire)"""
        return await self.key.expire(key, ttl)
