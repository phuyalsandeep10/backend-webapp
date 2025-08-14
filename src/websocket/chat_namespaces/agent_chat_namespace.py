import json

import socketio

from src.models import Message, MessageAttachment, Conversation
from src.common.dependencies import get_user_by_token

# from src.config.broadcast import broadcast  # Replaced with direct Redis pub/sub

from src.config.settings import settings
from ..chat_utils import get_room_channel, user_notification_group, conversation_group
from src.config.redis.redis_listener import get_redis
from ..chat_redis import redis_publish

REDIS_URL = settings.REDIS_URL

chat_namespace = "/chat"

# Redis keys
REDIS_ROOM_KEY = "chat:room:"  # chat:room:{conversation_id} -> set of sids
REDIS_SID_KEY = "chat:sid:"  # chat:sid:{sid} -> conversation_id


# Redis helper






class AgentChatNamespace(socketio.AsyncNamespace):
    receive_message = "receive-message"
    receive_typing = "typing"
    stop_typing = "stop-typing"
    message_seen = "message_seen"
    chat_online = "chat_online"
    customer_land = "customer_land"

    def __init__(self):
        super().__init__("/agent-chat")
        self.rooms = {}

    async def _notify_to_customers(self, org_id: int):
        await redis_publish(
            channel=f"ws:{org_id}:customer_notification",
            message=json.dumps(
                {"event": self.chat_online, "mode": "online", "organization_id": org_id}
            ),
        )


    async def _join_org_user_group(self, org_id: int, sid: int):
        print(f"join room name {user_notification_group(org_id)} and sid {sid}")
        # redis = await get_redis()
        await self.enter_room(sid=sid, room=user_notification_group(org_id))
        # await redis.sadd(f"ws:{org_id}:user_sids:{user.id}", sid)
        # await redis.set(f"ws:{org_id}:sid_user:{sid}", user.id)

    async def _join_conversation(self, conversation_id: int, sid: int):
        redis = await get_redis()
        await redis.sadd(f'ws:user_conversation_sids:{conversation_id}', sid)
        await redis.set(f"ws:user_conversation:{sid}", conversation_id)
        self.enter_room(sid=sid, room=conversation_group(conversation_id))
    
    async def _leave_conversation(self, conversation_id: int, sid: int):
        redis = await get_redis()
        self.leave_room(sid=sid, room=conversation_group(conversation_id))
        await redis.srem(f'ws:user_conversation_sids:{conversation_id}', sid)
        await redis.delete(f"ws:user_conversation:{sid}")
    
    async def _leave_user_group(self, org_id: int, sid: int):
        self.leave_room(sid=sid, room=user_notification_group(org_id))
    
    
  

    async def on_connect(self, sid, environ, auth):
        print(f"🔌Agent Socket connection attempt: {sid}")
        if not auth:
            print("No auth data provided")
            return False

        token = auth.get("token")
        user = await get_user_by_token(token)
        if not user:
            print("Invalid token provided")
            return False

        organization_id = user.attributes.get("organization_id")


        if not organization_id:
            print("User has no organization_id")
            return False

        await self._join_org_user_group(organization_id, sid)
        # notify customers in the same workspace that a user has connected
        await self._notify_to_customers(organization_id)
        print(
            f"User {user.id} connected with sid {sid} in workspace {organization_id}"
        )
        return True

    


    async def on_join_conversation(self, sid, data):
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return
        await self._join_conversation(conversation_id, sid)
    
    async def on_leave_conversation(self, sid, data):
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return False
        await self._leave_conversation(conversation_id, sid)
    

    async def on_message(self, sid, data):
        print(f"on message {data} and sid {sid}")
        
        conversation_id = data.get('conversation_id')
        organization_id = data.get('organization_id')


     
        
        if not conversation_id:
            return
        

        try:
            print(f'emit to room conversation {get_room_channel(conversation_id)}')
            channel_name = get_room_channel(conversation_id)
            if not data.get('user_id'):
                redis = await get_redis()
                sids = await redis.smembers(f"ws:{organization_id}:conversation_sids:{conversation_id}")
                print("SIDs in this conversation:", [sid.decode() for sid in sids])
                if not sids:
                    channel_name = user_notification_group(organization_id)
                else:
                    channel_name = conversation_group(conversation_id)
            print(f'message channel {channel_name}')
            await redis_publish(
                channel=channel_name,
                message=json.dumps(
                    {
                        "event": self.receive_message,
                        "sid": sid,
                        "message": data.get("message"),
                        "uuid": data.get("uuid"),
                        "status":data.get('status','SENT'),#delivered, SENT and seen
                        "user_id": data.get("user_id"),
                        "files": data.get("files", []),
                        "organization_id": organization_id,
                        "mode":"message"
                    }
                ),
            )
        except Exception as e:
            print(f"Error publishing message to Redis: {e}")
        
 

    async def on_message_seen(self, sid, data):
        redis = await get_redis()
        conversation_id = await redis.get(f"{REDIS_SID_KEY}{sid}")
        if not conversation_id:
            return

        await redis_publish(
            channel=get_room_channel(conversation_id),
            message=json.dumps(
                {"event": self.message_seen, "sid": sid, "uuid": data.get("uuid")}
            ),

        )

    async def on_typing(self, sid, data):
        redis = await get_redis()
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return

        await redis_publish(
            channel=get_room_channel(conversation_id),
            message=json.dumps(
                {
                    "event": self.receive_typing,
                    "sid": sid,
                    "message": data.get("message", ""),
                    "mode": data.get("mode", "typing"),
                }
            ),
        )

    async def on_stop_typing(self, sid,data):
        print(f"on stop typing  sid {sid} and {data}")
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return

        await redis_publish(
            channel=get_room_channel(conversation_id),
            message=json.dumps(
                {"event": self.stop_typing, "sid": sid, "mode": "stop-typing"}
            ),
        )

    async def on_disconnect(self, sid,auth):
        customer_id = auth.get('customer_id')
        conversation_id = auth.get('conversation_id')
        organization_id = auth.get('organization_id')
        user_id = auth.get('user_id')
        redis = await get_redis()
        if customer_id:
            await redis.srem(f"ws:{organization_id}:conversation_sids:{conversation_id}", sid)
            await redis.delete(f"ws:{organization_id}:sid_conversation:{sid}")
            await self._leave_customer_group(organization_id, sid)
        if user_id:
            await redis.srem(f"ws:{organization_id}:user_sids:{user_id}", sid)
            await redis.delete(f"ws:{organization_id}:sid_user:{sid}")
            await self._leave_user_group(organization_id, sid)

        
        redis = await get_redis()
        conversation_id = await redis.get(f"{REDIS_SID_KEY}{sid}")
        if conversation_id:
            await redis.srem(f"{REDIS_ROOM_KEY}{conversation_id}", sid)
            await redis.delete(f"{REDIS_SID_KEY}{sid}")
            print(f"❌ Disconnected {sid} from conversation {conversation_id}")
