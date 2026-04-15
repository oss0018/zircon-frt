import json
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    client = await get_redis()
    await client.set(key, json.dumps(value), ex=ttl)


async def cache_get(key: str) -> Any | None:
    client = await get_redis()
    data = await client.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_delete(key: str) -> None:
    client = await get_redis()
    await client.delete(key)
