import json

import socketio

from src.config.redis.redis_listener import get_redis


class BaseNameSpace(socketio.AsyncNamespace):
    def __init__(self, namespace: str):
        super().__init__(namespace=namespace)
        self.redis = None

    async def get_redis(self):
        if self.redis is None:
            self.redis = await get_redis()
        return self.redis

    async def redis_publish(self, channel: str, message: dict):
        """Direct Redis pub/sub publish - more reliable than broadcaster library"""

        redis_client = await self.get_redis()

        try:
            result = await redis_client.publish(channel, json.dumps(message))
            print(f"📡 Published to Redis channel '{channel}': {result} subscribers")
            return result
        except Exception as e:
            print(f"❌ Redis publish failed: {e}")
            return 0
