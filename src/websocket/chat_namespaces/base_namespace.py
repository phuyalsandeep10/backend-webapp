import socketio
from src.config.redis.redis_listener import get_redis
from src.services.redis_service import RedisService


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

        await RedisService.redis_publish(channel=channel, message=message)
