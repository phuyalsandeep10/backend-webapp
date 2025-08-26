from src.services.redis_service import RedisService
from .base_namespace import BaseNameSpace
from ..chat_utils import ChatUtils
from ..channel_names import TYPING_CHANNEL, TYPING_STOP_CHANNEL, MESSAGE_SEEN_CHANNEL, AGENT_JOIN_CONVERSATION_CHANNEL, AGENT_AVAILABILITY_CHANNEL


REDIS_SID_KEY = "ws:chat:sid:"  # chat:sid:{sid} -> conversation_id
REDIS_ROOM_KEY = "ws:chat:room:"  # chat:room:{conversation_id} -> set of sids




class BaseChatNamespace(BaseNameSpace):
    receive_message = "receive-message"
    receive_typing = "typing"
    stop_typing = "stop-typing"
    message_seen = "message_seen"
    chat_online = "chat_online"
    _join_conversation = 'join_conversation'
    customer_land = "customer_land"
    message_notification = "message-notification"
    is_customer: bool = False

    def __init__(self, namespace: str, is_customer: bool = False):
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
        result = await redis.get(self._conversation_from_sid(sid))
        return result.decode("utf-8") if result else None

    async def get_conversation_sid(self, sid):
        redis = await self.get_redis()
        return await redis.get(self._conversation_from_sid(sid))

    async def get_conversation_sids(self, conversationId: int):
        redis = await self.get_redis()
        sids = await redis.smembers(self._conversation_add_sid(conversationId))
        return [sid.decode("utf-8") for sid in sids] if sids else []

    async def join_group(self, conversation_id, sid):
        await self.enter_room(
            sid=sid,
            room=ChatUtils.conversation_group(conversation_id),
            namespace=self.namespace,
        )

    async def join_conversation(self, conversationId, sid):
        redis = await self.get_redis()

        await self.join_group(conversationId, sid)

        await self.redis_publish(
            channel=AGENT_JOIN_CONVERSATION_CHANNEL,
            message={
                "event": self._join_conversation,
                "mode": "online",
                "conversation_id": conversationId,
                "sid": sid,
            },
        )

        await redis.sadd(self._conversation_add_sid(conversationId), sid)
        await redis.set(self._conversation_from_sid(sid), conversationId)
        
        # Notify customers that an agent has joined
        await self._notify_agent_available(conversationId, len(await self.get_conversation_sids(conversationId)))

    async def leave_conversation(self, conversationId: int, sid: int):
        redis = await self.get_redis()
    
        await self.leave_room(
            sid=sid,
            room=ChatUtils.conversation_group(conversationId),
            namespace=self.namespace,
        )
        await redis.srem(self._conversation_add_sid(conversationId), sid)

        await redis.delete(self._conversation_from_sid(sid))
        
        # Check if this was the last agent to leave and notify customers
        await self._check_agent_availability(conversationId)

    async def on_typing(self, sid, data: dict):
        conversation_id = data.get('conversation_id')
        organization_id = data.get("organization_id")
        
        if not conversation_id or not organization_id:
            return False

        await self.redis_publish(
            channel=TYPING_CHANNEL,
            message={
                "event": self.receive_typing,
                "sid": sid,
                "message": data.get("message", ""),
                "mode": data.get("mode", "typing"),
                "conversation_id": conversation_id,
                "organization_id": organization_id,
                "is_customer": self.is_customer,
            },
        )

    async def on_stop_typing(self, sid, data: dict):
        conversation_id = data.get('conversation_id')
        print(f"conversation id {conversation_id}")

        if not conversation_id:
            return False

        await self.redis_publish(
            channel=TYPING_STOP_CHANNEL,
            message={
                "event": self.stop_typing,
                "sid": sid,
                "mode": "stop-typing",
                "conversation_id": conversation_id,
                "is_customer": self.is_customer,
            },
        )

    async def on_message_seen(self, sid, data: dict):
        print(f"message seen {sid}")
        messageId = data.get("message_id")
        
        if not messageId:
            return False
        
        message = await ChatUtils.save_message_seen(messageId)
        if not message:
            return False
            
        await self.redis_publish(
            channel=MESSAGE_SEEN_CHANNEL,
            message={
                "event": "message_seen",
                "conversation_id": message.conversation_id,
                "message_id": messageId,
                "is_customer": not message.user_id , # If no user_id, it's a customer message,
                "sid": sid
            },
        )

    async def _check_agent_availability(self, conversation_id: int):
        """Check if agents are available in a conversation and notify customers accordingly"""
        try:
            # Get all agent SIDs in this conversation
            agent_sids = await self.get_conversation_sids(conversation_id)
            
            # Check if any agents are still in the conversation
            if not agent_sids:
                # No agents available, notify customers
                await self._notify_agent_unavailable(conversation_id, "no_agents")
            else:
                # Agents are available, notify customers
                await self._notify_agent_available(conversation_id, len(agent_sids))
                
        except Exception as e:
            print(f"⚠️ Error checking agent availability: {e}")

    async def _notify_agent_unavailable(self, conversation_id: int, reason: str):
        """Notify customers that no agents are available"""
        try:
            await self.redis_publish(
                channel=AGENT_AVAILABILITY_CHANNEL,
                message={
                    "event": self.message_notification,
                    "conversation_id": conversation_id,
                    "status": "unavailable",
                    "reason": reason,
                    "message": "No agents are currently available to assist you. Please wait for an agent to join.",
                    "timestamp": self._get_current_timestamp()
                }
            )
            print(f"✅ Notified customers that agents are unavailable in conversation {conversation_id}")
        except Exception as e:
            print(f"⚠️ Error notifying agent unavailability: {e}")

    async def _notify_agent_available(self, conversation_id: int, agent_count: int):
        """Notify customers that agents are available"""
        try:
            await self.redis_publish(
                channel=AGENT_AVAILABILITY_CHANNEL,
                message={
                    "event": self.message_notification,
                    "conversation_id": conversation_id,
                    "status": "available",
                    "agent_count": agent_count,
                    "message": f"{agent_count} agent(s) are now available to assist you.",
                    "timestamp": self._get_current_timestamp()
                }
            )
            print(f"✅ Notified customers that {agent_count} agent(s) are available in conversation {conversation_id}")
        except Exception as e:
            print(f"⚠️ Error notifying agent availability: {e}")

    def _get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    async def check_all_conversations_agent_availability(self):
        """Check agent availability for all active conversations"""
        try:
            from src.modules.chat.models.conversation import Conversation
            
            # Get all active conversations
            conversations = await Conversation.filter(where={"is_resolved": False})
            
            for conversation in conversations:
                await self._check_agent_availability(conversation.id)
                
            print(f"✅ Checked agent availability for {len(conversations)} conversations")
            
        except Exception as e:
            print(f"⚠️ Error checking all conversations agent availability: {e}")

    async def schedule_agent_availability_check(self):
        """Schedule periodic agent availability checks"""
        import asyncio
        
        while True:
            try:
                await self.check_all_conversations_agent_availability()
                # Wait for 5 minutes before next check
                await asyncio.sleep(300)
            except Exception as e:
                print(f"⚠️ Error in scheduled agent availability check: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def get_agent_workload_info(self, conversation_id: int):
        """Get information about agent workload and availability"""
        try:
            # Get all agent SIDs in this conversation
            current_agents = await self.get_conversation_sids(conversation_id)
            
            # Get total active conversations
            from src.modules.chat.models.conversation import Conversation
            total_conversations = await Conversation.filter(where={"is_resolved": False})
            
            # Count conversations with agents
            conversations_with_agents = 0
            total_agents_working = 0
            
            for conv in total_conversations:
                conv_agents = await self.get_conversation_sids(conv.id)
                if conv_agents:
                    conversations_with_agents += 1
                    total_agents_working += len(conv_agents)
            
            return {
                "current_conversation_agents": len(current_agents),
                "total_active_conversations": len(total_conversations),
                "conversations_with_agents": conversations_with_agents,
                "total_agents_working": total_agents_working,
                "agents_available": len(current_agents) > 0
            }
            
        except Exception as e:
            print(f"⚠️ Error getting agent workload info: {e}")
            return None
