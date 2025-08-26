from .redis_service import RedisService
from src.socket_config import sio
from src.websocket.chat_utils import ChatUtils
from src.websocket.chat_namespace_constants import CUSTOMER_CHAT_NAMESPACE

class ConversationService:
    @staticmethod
    async def set_customer_sid(sid:str,customer_id:int):
        redis = await RedisService.get_redis()
        await redis.set(f"customer_id:{customer_id}",sid)

    @staticmethod
    async def get_customer_sid(customer_id:int):
        redis = await RedisService.get_redis()
        result = await redis.get(f"customer_id:{customer_id}")
        return result.decode('utf-8') if result else None

    @staticmethod
    async def join_customer_room(sid,conversation_id):
        try:
            print(f"join customer room {sid} {conversation_id}")
            await sio.enter_room(sid=sid, room=ChatUtils.conversation_group(conversation_id), namespace=CUSTOMER_CHAT_NAMESPACE)
        except Exception as e:
            print(f"❌ Join customer room failed: {e}")

    @staticmethod
    async def leave_customer_room(sid,conversation_id):
        await sio.leave_room(sid=sid, room=ChatUtils.conversation_group(conversation_id), namespace=CUSTOMER_CHAT_NAMESPACE)
