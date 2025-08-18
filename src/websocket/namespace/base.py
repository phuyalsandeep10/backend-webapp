import asyncio
import logging
from typing import Any

import socketio

from src.common.dependencies import get_user_by_token

logger = logging.getLogger(__name__)


class BaseNameSpace(socketio.AsyncNamespace):
    def __init__(self, namespace: str, sio: socketio.AsyncServer, redis):
        super().__init__(namespace)
        self.namespace = namespace
        self.sio = sio
        self.redis = redis

    async def on_connect(self, sid, environ, auth):
        token = auth.get("token")
        if not token:
            return False  # reject the connection
        user = await get_user_by_token(token)
        print("The user", user)
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

    async def publish(self, channel: str, message: dict[str, Any]):
        await self.redis.publish(channel, message)

    async def subscribe(self, channel: str):
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
