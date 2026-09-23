"""
Redis connection client.
Used for rate-limiting (Step 2) and later for caching. A single shared
client is created once here and imported everywhere else it's needed.
"""

import redis

from app.core.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,  # returns strings instead of bytes — easier to work with
)