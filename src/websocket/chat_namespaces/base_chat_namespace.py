from .base_namespace import BaseNameSpace
from ..chat_utils import ChatUtils
from ..channel_names import TYPING_CHANNEL,TYPING_STOP_CHANNEL,MESSAGE_SEEN_CHANNEL
from ..chat_namespace_constants import CUSTOMER_CHAT_NAMESPACE


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
    is_customer:bool=False

    def __init__(self, namespace: str,is_customer:bool=False):
        super().__init__(namespace)
        self.is_customer = is_customer

    async def on_disconnect(self, sid):
        # on disconnect
        await self.disconnect(sid)
        conversation_id = await self._get_conversation_id_from_sid(sid)
        if not conversation_id:
            return False
        await self.leave_conversation(conversation_id, sid)

    async def save_message_db(self, conversation_id: int, data: dict):
        await ChatUtils.save_message_db(conversation_id, data)


    def _conversation_add_sid(self, conversationId: int):
        return f"{REDIS_SID_KEY}:{conversationId}"

    def _conversation_from_sid(self, sid: int):
        # on connect
        return f"{REDIS_SID_KEY}:{sid}"
    
    async def _get_conversation_id_from_sid(self, sid: int):
        redis = await self.get_redis()
        result =  await redis.get(self._conversation_from_sid(sid))
        return result.decode("utf-8") if result else None
    
    async def get_conversation_sid(self,sid):
        redis = await self.get_redis()
        return await redis.get(self._conversation_from_sid(sid))

    
    async def get_conversation_sids(self, conversationId: int):
        redis = await self.get_redis()
        sids =  await redis.smembers(self._conversation_add_sid(conversationId))
        return [sid.decode("utf-8") for sid in sids] if sids else []
        


    async def join_conversation(self, conversationId, sid):

        redis = await self.get_redis()

        await self.enter_room(sid=sid, room=ChatUtils.conversation_group(conversationId),namespace=self.namespace)

        await redis.sadd(self._conversation_add_sid(conversationId), sid)
        await redis.set(self._conversation_from_sid(sid), conversationId)

    async def leave_conversation(self, conversationId: int, sid: int):
        redis = await self.get_redis()

        await self.leave_room(sid=sid, room=ChatUtils.conversation_group(conversationId),namespace=self.namespace)
        await redis.srem(self._conversation_add_sid(conversationId), sid)

        await redis.delete(self._conversation_from_sid(sid))

    

    
    async def on_typing(self, sid,data:dict):
        conversation_id = await self._get_conversation_id_from_sid(sid)
        if not conversation_id:
            return False

        
        
        await self.redis_publish(
            channel=TYPING_CHANNEL,
            message={
                "event": self.receive_typing,
                "sid": sid,
                "message": data.get("message", ""),
                "mode": data.get("mode", "typing"),
                "conversation_id": conversation_id,
                "organization_id": data.get("organization_id"),
                "is_customer": self.is_customer,
                "sid": sid
            },
        )

    async def on_stop_typing(self, sid):
        conversation_id = await self._get_conversation_id_from_sid(sid)
        
        if not conversation_id:
            return False
       


        await self.redis_publish(
            channel=TYPING_STOP_CHANNEL,
            message={"event": self.stop_typing, "sid": sid, "mode": "stop-typing","conversation_id": conversation_id,"is_customer": self.is_customer,"sid": sid},
            
        )

    async def on_message_seen(self, sid,data:dict):
        conversation_id = await self._get_conversation_id_from_sid(sid)
        messageId = data.get("message_id")

        if not conversation_id or not messageId:
            return False
        

        await self.redis_publish(
            channel=MESSAGE_SEEN_CHANNEL,
            message={"event": self.message_seen, "sid": sid, "message_id": messageId,"conversation_id":conversation_id}
        )
        
        
        await ChatUtils.save_message_seen(int(conversation_id), messageId)

