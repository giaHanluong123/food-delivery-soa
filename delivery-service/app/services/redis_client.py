import redis

from app.core.config import REDIS_DB, REDIS_HOST, REDIS_PORT


def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )