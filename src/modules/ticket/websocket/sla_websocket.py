import logging
from typing import List

import socketio

from src.modules.auth.models import User

logger = logging.getLogger(__name__)


class AlertNameSpace(socketio.AsyncNamespace):

    def __init__(self, namespace):
        super().__init__(namespace)
        self.user_ids: dict = {}

    async def on_connect(self, sid, environ, auth):
        if auth:
            user_id = auth.get("user_id")
            logger.info(f"Client connected to /alert namespace {user_id}")
            self.user_ids[user_id] = sid

    def on_disconnect(self, sid):
        logger.info(f"Client disconnected to /alert namespace {sid}")
