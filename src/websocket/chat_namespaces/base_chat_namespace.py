from .base_namespace import BaseNameSpace
from ..chat_utils import user_conversation_group, get_room_channel


REDIS_SID_KEY = "ws:chat:sid:"  # chat:sid:{sid} -> conversation_id
REDIS_ROOM_KEY = "ws:chat:room:"  # chat:room:{conversation_id} -> set of sids


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

    def _conversation_add_sid(self, conversationId: int):
        return f"{REDIS_SID_KEY}:{conversationId}"

    def _conversation_from_sid(self, sid: int):
        # on connect
        return f"{REDIS_SID_KEY}:{sid}"
    
    async def _get_conversation_id_from_sid(self, sid: int):
        redis = await self.get_redis()
        return await redis.get(self._conversation_from_sid(sid))
    
    async def get_conversation_sid(self,sid):
        redis = await self.get_redis()
        return await redis.get(self._conversation_from_sid(sid))

    
    async def get_converstion_sids(self, conversationId: int):
        redis = await self.get_redis()
        sids =  await redis.smembers(self._conversation_add_sid(conversationId))
        return [sid.decode("utf-8") for sid in sids] if sids else []
        


    async def join_conversation(self, conversationId, sid):

        redis = await self.get_redis()

        await self.enter_room(sid=sid, room=user_conversation_group(conversationId))

        await redis.sadd(self._conversation_add_sid(conversationId), sid)
        await redis.set(self._conversation_from_sid(sid), conversationId)

    async def leave_conversation(self, conversationId: int, sid: int):
        redis = await self.get_redis()

        await self.leave_room(sid=sid, room=user_conversation_group(conversationId))
        await redis.srem(self._conversation_add_sid(conversationId), sid)

        await redis.delete(self._conversation_from_sid(sid))

    
    async def on_message_seen(self, sid, data:dict):
        conversation_id = await self._get_conversation_id_from_sid(sid)
        if not conversation_id:
            return False

        await self.redis_publish(
            channel=get_room_channel(conversation_id),
            message={"event": self.message_seen, "sid": sid, "uuid": data.get("uuid")}
        )
    
    async def on_typing(self, sid,data:dict):
        conversation_id = await self._get_conversation_id_from_sid(sid)
        if not conversation_id:
            return False

        await self.redis_publish(
            channel=get_room_channel(conversation_id),
            message={
                "event": self.receive_typing,
                "sid": sid,
                "message": data.get("message", ""),
                "mode": data.get("mode", "typing"),
            },
      
        )

    async def on_stop_typing(self, sid):
        conversation_id = await self._get_conversation_id_from_sid(sid)
        if not conversation_id:
            return False

        await self.redis_publish(
            channel=get_room_channel(conversation_id),
            message={"event": self.stop_typing, "sid": sid, "mode": "stop-typing"},
            
        )

