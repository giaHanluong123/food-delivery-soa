import redis

# Kết nối Redis (tên host = redis vì Docker Compose)
redis_client = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True
)