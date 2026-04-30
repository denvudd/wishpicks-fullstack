import logging

from redis.asyncio import Redis

from app.core.settings import settings

logger = logging.getLogger(__name__)

_redis: Redis | None = None


async def get_redis_client() -> Redis | None:
    global _redis
    if _redis is None:
        try:
            _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            await _redis.ping()
        except Exception as exc:
            logger.error("Redis connection failed: %s", exc)
            _redis = None
    return _redis
