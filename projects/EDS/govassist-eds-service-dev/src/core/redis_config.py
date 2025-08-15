from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from src.core.config import configs


class SerializationMethod(Enum):
    JSON = "json"
    PICKLE = "pickle"
    NONE = "none"


@dataclass
class RedisConfig:
    """Redis configuration for the application"""

    # Connection string for Azure Redis Cache (alternative approach)
    connection_string: Optional[str] = configs.REDIS_URL

    # SSL/TLS settings for Azure Redis Cache
    ssl: bool = True
    ssl_cert_reqs: str = "CERT_NONE"  # For Azure Redis Cache

    # Connection pool settings
    max_connections: int = configs.REDIS_MAX_CONNECTIONS
    connection_timeout: float = 10.0
    socket_timeout: float = 10.0
    socket_keepalive: bool = True
    socket_keepalive_options: Dict = field(default_factory=dict)

    # Retry settings
    retry_on_timeout: bool = True
    retry_attempts: int = 5
    retry_backoff_base: float = 0.5
    retry_backoff_cap: float = 10.0

    # Health check settings
    health_check_interval: int = 60

    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: float = 60.0

    # Default TTL
    default_ttl: int = configs.REDIS_DEFAULT_TTL

    # Serialization
    default_serialization: SerializationMethod = SerializationMethod.JSON
