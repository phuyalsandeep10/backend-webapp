from src.config.redis.redis_listener import get_redis
import json


class RedisService:

    @staticmethod
    async def get_redis():
        redis = await get_redis()
        return redis

    @staticmethod
    async def redis_publish(channel: str, message: dict):
        """Direct Redis pub/sub publish - more reliable than broadcaster library"""

        redis_client = await get_redis()

        try:
            result = await redis_client.publish(channel, json.dumps(message))
            print(f"📡 Published to Redis channel '{channel}': {result} subscribers")
            return result
        except Exception as e:
            print(f"❌ Redis publish failed: {e}")
            return 0
    

