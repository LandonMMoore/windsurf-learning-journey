from slowapi import Limiter

from src.core.config import configs
from src.util.utils import user_or_ip_key

limiter = Limiter(
    key_func=user_or_ip_key, default_limits=["25/minute"], storage_uri=configs.REDIS_URL
)
