import asyncio
import json
import logging
from typing import Any

import redis.asyncio as redis
import socketio

from src.common.dependencies import get_user_by_token
from src.config.settings import settings

logger = logging.getLogger(__name__)


class BaseNameSpace(socketio.AsyncNamespace):
    def __init__(self, namespace: str, sio: socketio.AsyncServer):
        super().__init__(namespace)
        self.namespace = namespace
        self.sio = sio
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=False)

    async def on_connect(self, sid, environ, auth):
        token = auth.get("token")
        if not token:
            return False  # reject the connection
        user = await get_user_by_token(token)
        if not user:
            return False  # reject the connection
        await self.sio.save_session(sid, {"user": user}, namespace=self.namespace)
        logger.info(f"User {user.email} connected on {self.namespace} ")

    async def on_disconnect(self, sid):
        session = await self.sio.get_session(sid, namespace=self.namespace)
        user = session.get("user") if session else None
        if user:
            logger.info(f"User {user.email} disconnected from {self.namespace}")

    async def join_room(self, sid, room):
        await self.sio.enter_room(sid, room, namespace=self.namespace)

    async def leave_room(self, sid, room):
        await self.sio.leave_room(sid, room, namespace=self.namespace)

    async def redis_publish(self, channel: str, message: dict[str, Any]):
        try:
            result = await self.redis.publish(channel, json.dumps(message))
            logger.info(f"Published to Redis channel '{channel}': {result} subscribers")
            return result
        except Exception as e:
            logger.exception(f" Redis publish failed: {e}")

    async def redis_subscribe(self, channel: str):
        logger.info(f"Subscribing to {channel}")
        pubsub = self.redis.subscribe()
        await pubsub.subscribe(channel)

        async def reader():
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    data = msg["data"].decode()
                    logger.info(f"Redis -> {self.namespace} : {data}")
                    await self.emit(
                        "redis_message",
                        {"channel": channel, "data": data},
                        namespace=self.namespace,
                    )

        asyncio.create_task(reader())
