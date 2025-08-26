import socketio
from ..chat_namespace_constants import AGENT_CHAT_NAMESPACE, CUSTOMER_CHAT_NAMESPACE
from ..chat_utils import ChatUtils
from ..channel_names import (
    AGENT_NOTIFICATION_CHANNEL,
    MESSAGE_CHANNEL,
    TYPING_CHANNEL,
    TYPING_STOP_CHANNEL,
    MESSAGE_SEEN_CHANNEL,
    AGENT_JOIN_CONVERSATION_CHANNEL,
    AGENT_AVAILABILITY_CHANNEL
)



class ChatSubscriber:
    agent_namespace = AGENT_CHAT_NAMESPACE
    customer_namespace = CUSTOMER_CHAT_NAMESPACE
    

    def __init__(
        self, sio: socketio.AsyncServer, namespace: str = None, payload: dict = {}
    ):
        # print(f"chat subscriber payload {payload} and type {type(payload)}")
        self.sio = sio
        self.payload = payload
        self.event = payload.get("event")
        self.namespace = namespace

    async def emit(self, room: str, namespace: str = None, sid: str = None):
        namespace = namespace if namespace else self.namespace
        print(f"emit to room {room} ")
        print(f"emit to namespace {namespace}")
        print(f"emit to event {self.event}")
        print(f"skip to sid {sid}")
        
        # print(f"emit to payload {self.payload}")
        
        try:
            result = await self.sio.emit(
                event=self.event,
                room=room,
                data=self.payload,
                namespace=namespace,
                skip_sid=sid,
            )
            print(f"✅ Emitted event '{self.event}' to room '{room}' in namespace '{namespace}'")
            return result
        except Exception as e:
            print(f"❌ Emit failed: {e}")
            return None

    async def agent_notification(self):
        print("📢 Agent notification broadcast")
        room_name = ChatUtils.user_notification_group(
            org_id=self.payload.get("organization_id")
        )
        await self.emit(room_name, namespace=self.agent_namespace)

    async def customer_notification(self):
        print("📢 Customer notification broadcast")
        room_name = ChatUtils.customer_notification_group(
            org_id=self.payload.get("organization_id")
        )
        await self.emit(room_name, namespace=self.customer_namespace)

    async def agent_message_broadcast(self):
        print("agent message broadcast")
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )

        await self.emit(
            room_name, namespace=self.agent_namespace, sid=self.payload.get("sid")
        )

    async def customer_message_broadcast(self):
        print("customer message broadcast")
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )
        sids = self.sio.manager.rooms.get(self.customer_namespace, {}).get(room_name, set())
        print(f"sids in room {room_name}: {sids}")
        
        # Skip the sender if sid is provided
        skip_sid = self.payload.get("sid")
        await self.emit(room_name, namespace=self.customer_namespace, sid=skip_sid)

    async def broadcast_conversation(self):
        is_customer = self.payload.get("is_customer")
        print(f"Broadcasting conversation - is_customer: {is_customer}")
        
        if is_customer:
            print("Customer message - broadcasting to agents only")
            return await self.agent_message_broadcast()

        print("Agent message - broadcasting to both customers and agents")
        await self.customer_message_broadcast()
        await self.agent_message_broadcast()
    
    async def agent_join_conversation(self):
        print("👥 Agent join conversation broadcast")
        await self.agent_message_broadcast()

    async def agent_availability_notification(self):
        """Handle agent availability notifications"""
        print("👥 Processing agent availability notification")
        
        conversation_id = self.payload.get("conversation_id")
        status = self.payload.get("status")
        message = self.payload.get("message")
        
        if not conversation_id:
            print("⚠️ No conversation_id in agent availability payload")
            return
            
        # Broadcast to customers in the conversation room
        room_name = ChatUtils.conversation_group(conversation_id)
        
        # Send notification to customers
        await self.emit(
            room_name, 
            namespace=self.customer_namespace, 
            sid=None
        )
        
        print(f"✅ Agent availability notification sent to conversation {conversation_id}: {status}")

    async def message(self):
        print(f"📨 Processing message event: {self.event}")
        print(f"📨 Message payload: {self.payload}")
        
        # Check if this is a customer message and check agent availability
        if self.payload.get("is_customer"):
            await self._check_and_notify_agent_availability()
        
        await self.broadcast_conversation()

    async def _check_and_notify_agent_availability(self):
        """Check if agents are available in the conversation and notify customer if not"""
        try:
            conversation_id = self.payload.get("conversation_id")
            if not conversation_id:
                return
                
            # Get the agent namespace instance to check availability
            from ..chat_namespaces.agent_chat_namespace import AgentChatNamespace
            
            # Create a temporary instance to check availability
            agent_ns = AgentChatNamespace("/agent-chat")
            
            # Check if any agents are in this conversation
            agent_sids = await agent_ns.get_conversation_sids(conversation_id)
            
            if not agent_sids:
                # No agents available, send immediate notification
                await self._send_agent_unavailable_notification(conversation_id)
                # Also notify all agents about the new customer message
                await self._notify_agents_about_customer_message(conversation_id)
            else:
                print(f"✅ {len(agent_sids)} agent(s) available in conversation {conversation_id}")
                
        except Exception as e:
            print(f"⚠️ Error checking agent availability for message: {e}")

    async def _send_agent_unavailable_notification(self, conversation_id: int):
        """Send immediate notification that no agents are available"""
        try:
            from datetime import datetime
            
            # Get agent workload information for better context
            workload_info = await self._get_agent_workload_context(conversation_id)
            
            # Create a more informative message based on workload
            if workload_info and workload_info.get("total_agents_working", 0) > 0:
                message = f"No agents are currently available in this conversation. {workload_info['total_agents_working']} agent(s) are working on {workload_info['conversations_with_agents']} other conversation(s). Your message has been sent and agents will be notified."
            else:
                message = "No agents are currently available in this conversation. Your message has been sent and agents will be notified."
            
            notification_payload = {
                "event": "message-notification",
                "conversation_id": conversation_id,
                "status": "unavailable",
                "reason": "no_agents_in_conversation",
                "message": message,
                "workload_info": workload_info,
                "timestamp": datetime.utcnow().isoformat(),
                "urgent": True
            }
            
            # Send notification to the customer in the conversation room
            room_name = ChatUtils.conversation_group(conversation_id)
            
            # Create a temporary subscriber for the notification
            temp_subscriber = ChatSubscriber(self.sio, payload=notification_payload)
            await temp_subscriber.emit(
                room_name, 
                namespace=self.customer_namespace, 
                sid=None
            )
            
            print(f"✅ Sent urgent agent unavailable notification to conversation {conversation_id}")
            
        except Exception as e:
            print(f"⚠️ Error sending agent unavailable notification: {e}")

    async def _get_agent_workload_context(self, conversation_id: int):
        """Get context about agent workload for better customer notifications"""
        try:
            from ..chat_namespaces.agent_chat_namespace import AgentChatNamespace
            
            # Create a temporary instance to get workload info
            agent_ns = AgentChatNamespace("/agent-chat")
            return await agent_ns.get_agent_workload_info(conversation_id)
            
        except Exception as e:
            print(f"⚠️ Error getting agent workload context: {e}")
            return None

    async def _notify_agents_about_customer_message(self, conversation_id: int):
        """Notify all agents about a new customer message in a conversation they're not in"""
        try:
            from datetime import datetime
            
            # Get customer info from the message payload
            customer_id = self.payload.get("customer_id")
            message_content = self.payload.get("content", "")
            
            notification_payload = {
                "event": "message-notification",
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "status": "new_customer_message",
                "message": f"New customer message in conversation {conversation_id}",
                "content_preview": message_content[:100] + "..." if len(message_content) > 100 else message_content,
                "timestamp": datetime.utcnow().isoformat(),
                "urgent": True,
                "requires_attention": True
            }
            
            # Send notification to all agents in the organization
            # This will go to the agent notification room
            org_id = self.payload.get("organization_id")
            if org_id:
                room_name = ChatUtils.user_notification_group(org_id)
                
                temp_subscriber = ChatSubscriber(self.sio, payload=notification_payload)
                await temp_subscriber.emit(
                    room_name, 
                    namespace=self.agent_namespace, 
                    sid=None
                )
                
                print(f"✅ Notified all agents about new customer message in conversation {conversation_id}")
            else:
                print(f"⚠️ No organization_id found for agent notification")
                
        except Exception as e:
            print(f"⚠️ Error notifying agents about customer message: {e}")

    async def typing(self):
        print("⌨️ Processing typing event")
        await self.broadcast_conversation()

    async def stop_typing(self):
        print("⏹️ Processing stop typing event")
        await self.broadcast_conversation()

    async def message_seen(self):
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )
        if self.payload.get("is_customer"):
            await self.emit(room_name, namespace=self.customer_namespace, sid=self.payload.get("sid"))
        else:
            await self.emit(room_name, namespace=self.agent_namespace, sid=self.payload.get("sid"))
        


async def chat_subscriber(sio: socketio.AsyncServer, channel: str, payload: dict):
    print(f"🔔 Chat subscriber called for channel: {channel}")
    print(f"🔔 Payload: {payload}")
    
    subscriber = ChatSubscriber(sio, payload=payload)
    
    # handle chat events
    if channel == AGENT_NOTIFICATION_CHANNEL:
        print("📢 Processing agent notification")
        await subscriber.agent_notification()

    elif channel == AGENT_JOIN_CONVERSATION_CHANNEL:
        print("👥 Processing agent join conversation")
        await subscriber.agent_join_conversation()

    elif channel == AGENT_AVAILABILITY_CHANNEL:
        print("👥 Processing agent availability notification")
        await subscriber.agent_availability_notification()

    elif channel == MESSAGE_CHANNEL:
        print("💬 Processing message")
        await subscriber.message()

    elif channel == TYPING_CHANNEL:
        print("⌨️ Processing typing")
        await subscriber.typing()

    elif channel == TYPING_STOP_CHANNEL:
        print("⏹️ Processing stop typing")
        await subscriber.stop_typing()

    elif channel == MESSAGE_SEEN_CHANNEL:
        print("👁️ Processing message seen")
        await subscriber.message_seen()
    
    else:
        print(f"⚠️ Unknown channel: {channel}")
