import asyncio
import json
import logging
import pickle
import ssl
import time
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from src.core.redis_config import RedisConfig, SerializationMethod

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple circuit breaker implementation"""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitBreakerState.CLOSED

    def can_execute(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time > self.timeout
            ):
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class RedisSerializer:
    """Handles serialization and deserialization of Redis values"""

    @staticmethod
    def serialize(
        value: Any, method: SerializationMethod = SerializationMethod.NONE
    ) -> str:
        """Serialize value based on method"""
        if method == SerializationMethod.JSON:
            return json.dumps(value)
        elif method == SerializationMethod.PICKLE:
            return pickle.dumps(value).decode("latin-1")
        else:
            return str(value)

    @staticmethod
    def deserialize(
        value: str, method: SerializationMethod = SerializationMethod.NONE
    ) -> Any:
        """Deserialize value based on method"""
        if method == SerializationMethod.JSON:
            return json.loads(value)
        elif method == SerializationMethod.PICKLE:
            return pickle.loads(value.encode("latin-1"))
        else:
            return value


class RedisConnectionManager:
    """Manages Redis connection pool and client"""

    def __init__(self, config: RedisConfig):
        self.config = config
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._initialized = False

    async def initialize(self):
        """Initialize Redis connection pool and client"""
        if self._initialized:
            logger.info("Redis connection already initialized")
            return

        if not self.config.connection_string:
            raise ValueError("Redis connection string is required")

        logger.info("Initializing Redis connection...")

        self.pool = ConnectionPool.from_url(
            self.config.connection_string,
            ssl_cert_reqs=getattr(ssl, self.config.ssl_cert_reqs, ssl.CERT_NONE),
            max_connections=self.config.max_connections,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.connection_timeout,
            socket_keepalive=self.config.socket_keepalive,
            socket_keepalive_options=self.config.socket_keepalive_options,
            retry_on_timeout=self.config.retry_on_timeout,
            retry=Retry(
                ExponentialBackoff(
                    base=self.config.retry_backoff_base,
                    cap=self.config.retry_backoff_cap,
                ),
                retries=self.config.retry_attempts,
            ),
        )

        self.client = redis.Redis(connection_pool=self.pool)
        await self.client.ping()
        self._initialized = True
        logger.info("✅ Redis connection established")

    async def close(self):
        """Close Redis connection and cleanup resources"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        self._initialized = False
        logger.info("Redis connection closed")

    @property
    def is_initialized(self) -> bool:
        return self._initialized and self.client is not None


class RedisClient:
    """Mature, simple async Redis client with OOP design"""

    def __init__(self, config: RedisConfig):
        self.config = config
        self.connection = RedisConnectionManager(config)
        self.serializer = RedisSerializer()
        self.circuit_breaker = CircuitBreaker(
            config.circuit_breaker_failure_threshold, config.circuit_breaker_timeout
        )
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_healthy = True

    async def initialize(self):
        """Initialize the Redis client"""
        await self.connection.initialize()
        self._start_health_check()

    async def close(self):
        """Close the Redis client"""
        if self._health_check_task:
            self._health_check_task.cancel()
        await self.connection.close()

    def _start_health_check(self):
        """Start health check loop"""
        self._health_check_task = asyncio.create_task(self._health_check_loop())

    async def _health_check_loop(self):
        """Continuous health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                if self.connection.client:
                    await self.connection.client.ping()
                    if not self._is_healthy:
                        self._is_healthy = True
                        logger.info("Redis health check: HEALTHY")
            except Exception as e:
                if self._is_healthy:
                    self._is_healthy = False
                    logger.error(f"Redis health check failed: {e}")

    async def _execute_with_circuit_breaker(self, operation: Callable, *args, **kwargs):
        """Execute operation with circuit breaker pattern"""
        if not self.circuit_breaker.can_execute():
            raise redis.ConnectionError("Circuit breaker is OPEN")

        if not self.connection.is_initialized:
            await self.connection.initialize()

        if not self.connection.client:
            raise redis.ConnectionError("Redis client not initialized")

        try:
            result = await operation(*args, **kwargs)
            self.circuit_breaker.on_success()
            return result
        except Exception as e:
            self.circuit_breaker.on_failure()
            logger.error(f"Redis operation failed: {e}")
            raise

    # Core Operations
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialization: SerializationMethod = SerializationMethod.NONE,
    ) -> bool:
        """Set key-value pair with optional TTL"""
        serialized_value = self.serializer.serialize(value, serialization)
        if ttl and ttl > 0:
            return await self._execute_with_circuit_breaker(
                self.connection.client.set, key, serialized_value, ex=ttl
            )
        return await self._execute_with_circuit_breaker(
            self.connection.client.set, key, serialized_value
        )

    async def get(
        self, key: str, serialization: SerializationMethod = SerializationMethod.NONE
    ) -> Any:
        """Get value by key"""
        value = await self._execute_with_circuit_breaker(
            self.connection.client.get, key
        )
        if value is None:
            return None
        return self.serializer.deserialize(value.decode("utf-8"), serialization)

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.delete, *keys
        )

    async def exists(self, *keys: str) -> int:
        """Check if keys exist"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.exists, *keys
        )

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.expire, key, ttl
        )

    # Hash Operations
    async def hset(
        self,
        key: str,
        field: Optional[str] = None,
        value: Any = None,
        mapping: Optional[Dict[str, Any]] = None,
        serialization: SerializationMethod = SerializationMethod.NONE,
    ) -> int:
        """Set hash field(s)"""
        if mapping is not None:
            serialized_mapping = {
                k: self.serializer.serialize(v, serialization)
                for k, v in mapping.items()
            }
            return await self._execute_with_circuit_breaker(
                self.connection.client.hset, key, mapping=serialized_mapping
            )
        if field is not None and value is not None:
            serialized_value = self.serializer.serialize(value, serialization)
            return await self._execute_with_circuit_breaker(
                self.connection.client.hset, key, field, serialized_value
            )
        raise ValueError(
            "Either 'mapping' or both 'field' and 'value' must be provided"
        )

    async def hget(
        self,
        key: str,
        field: str,
        serialization: SerializationMethod = SerializationMethod.NONE,
    ) -> Any:
        """Get hash field value"""
        value = await self._execute_with_circuit_breaker(
            self.connection.client.hget, key, field
        )
        if value is None:
            return None
        return self.serializer.deserialize(value.decode("utf-8"), serialization)

    async def hgetall(
        self, key: str, serialization: SerializationMethod = SerializationMethod.NONE
    ) -> Dict[str, Any]:
        """Get all hash fields"""
        data = await self._execute_with_circuit_breaker(
            self.connection.client.hgetall, key
        )
        return {
            field.decode("utf-8"): self.serializer.deserialize(
                value.decode("utf-8"), serialization
            )
            for field, value in data.items()
        }

    # List Operations
    async def lpush(
        self,
        key: str,
        *values: Any,
        serialization: SerializationMethod = SerializationMethod.NONE,
    ) -> int:
        """Push values to left of list"""
        serialized_values = [
            self.serializer.serialize(v, serialization) for v in values
        ]
        return await self._execute_with_circuit_breaker(
            self.connection.client.lpush, key, *serialized_values
        )

    async def rpush(
        self,
        key: str,
        *values: Any,
        serialization: SerializationMethod = SerializationMethod.NONE,
    ) -> int:
        """Push values to right of list"""
        serialized_values = [
            self.serializer.serialize(v, serialization) for v in values
        ]
        return await self._execute_with_circuit_breaker(
            self.connection.client.rpush, key, *serialized_values
        )

    async def lrange(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
        serialization: SerializationMethod = SerializationMethod.NONE,
    ) -> List[Any]:
        """Get range of list elements"""
        values = await self._execute_with_circuit_breaker(
            self.connection.client.lrange, key, start, end
        )
        return [
            self.serializer.deserialize(v.decode("utf-8"), serialization)
            for v in values
        ]

    async def lpop(
        self, key: str, serialization: SerializationMethod = SerializationMethod.NONE
    ) -> Any:
        """Remove and return first element of list"""
        value = await self._execute_with_circuit_breaker(
            self.connection.client.lpop, key
        )
        if value is None:
            return None
        return self.serializer.deserialize(value.decode("utf-8"), serialization)

    async def rpop(
        self, key: str, serialization: SerializationMethod = SerializationMethod.NONE
    ) -> Any:
        """Remove and return last element of list"""
        value = await self._execute_with_circuit_breaker(
            self.connection.client.rpop, key
        )
        if value is None:
            return None
        return self.serializer.deserialize(value.decode("utf-8"), serialization)

    # Set Operations
    async def sadd(
        self,
        key: str,
        *values: Any,
        serialization: SerializationMethod = SerializationMethod.NONE,
    ) -> int:
        """Add members to set"""
        serialized_values = [
            self.serializer.serialize(v, serialization) for v in values
        ]
        return await self._execute_with_circuit_breaker(
            self.connection.client.sadd, key, *serialized_values
        )

    async def smembers(
        self, key: str, serialization: SerializationMethod = SerializationMethod.NONE
    ) -> List[Any]:
        """Get all set members"""
        values = await self._execute_with_circuit_breaker(
            self.connection.client.smembers, key
        )
        return [
            self.serializer.deserialize(v.decode("utf-8"), serialization)
            for v in values
        ]

    async def srem(self, key: str, *values: Any) -> int:
        """Remove members from set"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.srem, key, *values
        )

    async def sismember(self, key: str, value: Any) -> bool:
        """Check if value is in set"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.sismember, key, value
        )

    # Key Operations
    async def keys(self, pattern: str) -> List[str]:
        """Find keys matching pattern"""
        keys = await self._execute_with_circuit_breaker(
            self.connection.client.keys, pattern
        )
        return [key.decode("utf-8") for key in keys]

    async def ttl(self, key: str) -> int:
        """Get TTL of key"""
        return await self._execute_with_circuit_breaker(self.connection.client.ttl, key)

    async def type(self, key: str) -> str:
        """Get type of key"""
        key_type = await self._execute_with_circuit_breaker(
            self.connection.client.type, key
        )
        return key_type.decode("utf-8") if isinstance(key_type, bytes) else key_type

    # Sorted Set Operations
    async def zadd(self, key: str, mapping: Dict[Any, float]) -> int:
        """Add members to sorted set"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.zadd, key, mapping
        )

    async def zrange(
        self, key: str, start: int = 0, end: int = -1, withscores: bool = False
    ) -> List[Any]:
        """Get range of sorted set"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.zrange, key, start, end, withscores=withscores
        )

    async def zscore(self, key: str, member: Any) -> Optional[float]:
        """Get score of member in sorted set"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.zscore, key, member
        )

    async def zrem(self, key: str, *members: Any) -> int:
        """Remove members from sorted set"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.zrem, key, *members
        )

    # Distributed Locking
    async def acquire_lock(self, key: str, timeout: float = 10.0) -> bool:
        """Acquire distributed lock"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.set, key, "locked", nx=True, ex=int(timeout)
        )

    async def release_lock(self, key: str) -> bool:
        """Release distributed lock"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.delete, key
        )

    # Pipeline Operations
    @asynccontextmanager
    async def pipeline(self, transaction: bool = False):
        """Create pipeline for batch operations"""
        if not self.connection.is_initialized:
            await self.connection.initialize()

        pipe = self.connection.client.pipeline(transaction=transaction)
        try:
            yield pipe
            await pipe.execute()
        except Exception:
            raise
        finally:
            await pipe.reset()

    # Health and Monitoring
    async def ping(self) -> bool:
        """Ping Redis server"""
        try:
            if self.connection.client:
                await self.connection.client.ping()
                return True
        except Exception:
            pass
        return False

    @property
    def is_healthy(self) -> bool:
        """Check if Redis client is healthy"""
        return self._is_healthy

    @property
    def circuit_breaker_state(self) -> CircuitBreakerState:
        """Get circuit breaker state"""
        return self.circuit_breaker.state

    # Pub/Sub Operations
    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.publish, channel, message
        )

    async def subscribe(self, *channels: str):
        """Subscribe to channels"""
        if not self.connection.is_initialized:
            await self.connection.initialize()
        pubsub = self.connection.client.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub

    async def unsubscribe(self, pubsub, *channels: str):
        """Unsubscribe from channels"""
        await pubsub.unsubscribe(*channels)

    # Scan Operations
    async def scan(
        self, cursor: int = 0, match: Optional[str] = None, count: Optional[int] = None
    ):
        """Scan keys"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.scan, cursor, match=match, count=count
        )

    async def hscan(
        self,
        key: str,
        cursor: int = 0,
        match: Optional[str] = None,
        count: Optional[int] = None,
    ):
        """Scan hash fields"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.hscan, key, cursor, match=match, count=count
        )

    async def sscan(
        self,
        key: str,
        cursor: int = 0,
        match: Optional[str] = None,
        count: Optional[int] = None,
    ):
        """Scan set elements"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.sscan, key, cursor, match=match, count=count
        )

    async def zscan(
        self,
        key: str,
        cursor: int = 0,
        match: Optional[str] = None,
        count: Optional[int] = None,
    ):
        """Scan sorted set elements"""
        return await self._execute_with_circuit_breaker(
            self.connection.client.zscan, key, cursor, match=match, count=count
        )
