from .base_namespace import BaseNameSpace
from ..chat_utils import user_conversation_group


class BaseChatNamespace(BaseNameSpace):
    receive_message = "receive-message"
    receive_typing = "typing"
    stop_typing = "stop-typing"
    message_seen = "message_seen"
    chat_online = "chat_online"
    customer_land = "customer_land"
    message_notification = "message-notification"

    def __init__(self, namespace: str):
        super().__init__(namespace)

    def on_disconnect(self, sio):
        # on disconnect
        self.disconnect(sio)

    def _user_conversation_add_sid(self, conversationId: int):
        return f"ws:user_conversation_sids:{conversationId}"

    def _user_conversation_from_sid(self, sid: int):
        # on connect
        return f"ws:user_conversation:{sid}"

    async def user_join_conversation(self, conversationId, sid):

        redis = await self.get_redis()

        await self.enter_room(sid=sid, room=user_conversation_group(conversationId))

        await redis.sadd(self._user_conversation_from_sid(conversationId), sid)
        await redis.set(self._user_conversation_from_sid(sid), conversationId)

    async def user_leave_conversation(self, conversationId: int, sid: int):
        redis = await self.get_redis()

        await self.leave_room(sid=sid, room=user_conversation_group(conversationId))
        await redis.srem(self._user_conversation_from_sid(conversationId), sid)

        await redis.delete(self._user_conversation_from_sid(sid))
