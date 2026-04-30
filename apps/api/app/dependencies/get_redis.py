from redis.asyncio import Redis

from app.core.redis import get_redis_client


async def get_redis() -> Redis | None:
    return await get_redis_client()
