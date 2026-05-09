from redis.asyncio import Redis

async_redis_client = Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)