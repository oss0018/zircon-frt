import time
from collections import defaultdict
from threading import Lock

import redis.asyncio as aioredis


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            requests = self._requests[key]
            # Remove old requests outside window
            self._requests[key] = [t for t in requests if now - t < self.window_seconds]
            if len(self._requests[key]) >= self.max_requests:
                return False
            self._requests[key].append(now)
            return True


class RedisRateLimiter:
    """Async Redis-backed sliding window rate limiter per service."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    async def is_allowed(self, service: str, user_id: int, max_requests: int, window_seconds: int = 60) -> bool:
        key = f"rl:{service}:{user_id}"
        now = time.time()
        window_start = now - window_seconds
        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window_seconds * 2)
        results = await pipe.execute()
        count = results[2]
        return int(count) <= max_requests

    async def remaining(self, service: str, user_id: int, max_requests: int, window_seconds: int = 60) -> int:
        key = f"rl:{service}:{user_id}"
        now = time.time()
        window_start = now - window_seconds
        await self._redis.zremrangebyscore(key, "-inf", window_start)
        count = await self._redis.zcard(key)
        return max(0, max_requests - int(count))


rate_limiter = RateLimiter()

