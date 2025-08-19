
from src.config.redis.redis_listener import get_redis

async def redis_publish(channel: str, message: str):
    """Direct Redis pub/sub publish - more reliable than broadcaster library"""
    redis_client = await get_redis()
    try:
        result = await redis_client.publish(channel, message,namespace="/chat")
        print(f"📡 Published to Redis channel '{channel}': {result} subscribers")
        return result
    except Exception as e:
        print(f"❌ Redis publish failed: {e}")
        return 0