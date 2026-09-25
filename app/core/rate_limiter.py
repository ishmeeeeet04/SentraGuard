"""
Simple fixed-window rate limiter using Redis.
Each user gets a counter key like "ratelimit:<user_id>:<current_minute>".
The key auto-expires after 60 seconds, so it naturally resets every minute
without us having to clean anything up manually.
"""

import time

from app.core.redis_client import redis_client

MAX_REQUESTS_PER_MINUTE = 10


def is_rate_limited(user_id: str) -> bool:
    current_minute = int(time.time() // 60)
    key = f"ratelimit:{user_id}:{current_minute}"

    count = redis_client.incr(key)
    if count == 1:
        # first request in this window — set the key to expire in 60 seconds
        redis_client.expire(key, 60)

    return count > MAX_REQUESTS_PER_MINUTE