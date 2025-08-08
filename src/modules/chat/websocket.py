from fastapi import WebSocket, WebSocketDisconnect, Query, HTTPException, status
from src.app import app

import json

# from src.tasks import save_message_db
from src.models import Message, Conversation, MessageAttachment, User, Customer
from src.common.dependencies import get_user_by_token
from src.config.broadcast import broadcast
from fastapi.concurrency import run_until_first_complete
from typing import Optional


# from src.socket_config import sio
import socketio


chat_namespace = "/chat"


def get_room(conversationId: int):
    return f"conversation-{conversationId}"


async def ws_send(conversation_id: int, user_id: Optional[int] = None):
    room = get_room(conversationId=conversation_id)
    try:
        room = get_room(conversation_id)
        async with broadcast.subscribe(channel=room) as subscriber:
            async for event in subscriber:
                pass
                # data = json.loads(event.message)
                # if data.get("type") == "message":
                #     print("save messages in redis subscriber")
                #     save_messages.delay(
                #         conversation_id=conversation_id,
                #         data={"message": data.get("message")},
                #         user_id=user_id,
                #     )

                # await sio.emit(
                #     "response", {"data": "Chat received"}, room=room, namespace=chat_namespace
                # )
    except Exception as e:
        print(f"Exception in ws_send: {e}")


async def ws_recv(ws: WebSocket, conversation_id: int, user_id: Optional[int] = None):
    try:
        room = get_room(conversation_id)
        async for text in ws.iter_text():
            await broadcast.publish(channel=room, message=text)
    except Exception as e:
        print(f"Exception in ws_recv: {e}")


rooms = {}


conversations = {}


def get_conversation(conversation_id):
    return conversations.get(conversation_id)


def create_conversation(conversation_id, customer_id):
    conversation = {"customer_id": customer_id, "online": False, "sids": []}
    conversations[conversation_id] = conversation
    return conversation


def update_conversation(conversation_id, customer_id, online):
    conversation = get_conversation(conversation_id)
    if conversation:
        conversation["online"] = online
        conversation["customer_id"] = customer_id


async def save_message_db(
    conversation_id: int, data: dict, user_id: Optional[int] = None
):

    print("save message in db")
    conversation = await Conversation.get(conversation_id)
    replyId = data.get("reply_id")

    if not conversation:
        print(f"Conversation with Id {conversation_id} not found")

    return await Message.create(
        conversation_id=conversation_id,
        content=data.get("message"),
        customer_id=conversation.customer_id,
        user_id=user_id,
        reply_to_id=replyId,
    )


async def update_for_seen_db(messageId: int):
    return await Message.update(id=messageId, seen=True)


class ChatNamespace(socketio.AsyncNamespace):
    """WebSocket namespace for chat functionality."""

    receive_message = "recieve-message"
    receive_typing = "typing"
    stop_typing = "stop-typing"
    message_seen = "message_seen"
    chat_online = "chat_online"

    def __init__(self):
        super().__init__("/chat")
        self.rooms = {}

    async def on_connect_user(self,sid,environ,auth):
        print(f"on connect user connected: {sid}")
        if not auth:
            print("❌ No auth provided")
            return False

        token = auth.get("token")
        if not token:
            print("❌ No token provided")
            return False
        
        user = await get_user_by_token(token)

        if not user:
            print("❌ User not found")
            return False

        # user_id = auth.get("user_id")
        if token:
            
            await User.update(user.id,attributes={"is_online": True})
            print(f"User {user.id} is online")

            self.rooms[sid] = user.id
            user["sids"].append(sid)
            user["online"] = True
        

    async def on_connect(self, sid, environ, auth):
        print(f"Chat connected: {sid}")
        if not auth:
            print("❌ No auth provided")
            return False

        token = auth.get("token")

        # user_id = auth.get("user_id")
        if token:
            user = await get_user_by_token(token)
            await User.update(user.id,attributes={"is_online": True})
            print(f"User {user.id} is online")
        

            
        customer_id = auth.get("customer_id")
        if customer_id:
            await Customer.update(customer_id,is_online=True)
            print(f"Customer {customer_id} is online")
    
        conversation_id = auth.get("conversation_id")

        

        if not customer_id or not conversation_id:
            return False

        conversation = get_conversation(conversation_id)

        if not conversation:
            conversation = create_conversation(conversation_id, customer_id)

        self.rooms[sid] = conversation_id
        conversation["sids"].append(sid)


        conversation["online"] = True

        for si in conversation["sids"]:

            if si == sid:
                continue

            print(f"Sending message to {si} from {sid}")

            # save messages
            await self.emit(
                self.chat_online,
                {
                    "message": None,
                    "sid": sid,
                    "mode": "online",
                },
                room=si,
            )



        


        print(f"✅ Connected to /chat: {sid} (conversation_id: {conversation_id})")
        return True

    # async def on_message(self,sid,data):

    async def on_message(self, sid, data):
        conversation_id = self.rooms.get(sid)
        if not conversation_id:
            return

        conversation = get_conversation(conversation_id)

        print(f"conversation id {conversation_id} and conversation {conversation}")

        if not conversation:
            return
        # save_message_db.delay(conversation_id,data)

        for si in conversation["sids"]:

            if si == sid:
                continue

            print(f"Sending message to {si} from {sid}")

            # save messages
            await self.emit(
                self.receive_message,
                {
                    "message": data.get("message"),
                    "sid": sid,
                    "mode": "message",
                    "uuid": data.get("uuid"),
                    "seen": data.get("seen"),
                },
                room=si,
            )

        message = await save_message_db(
            conversation_id=conversation_id, data=data, user_id=data.get("user_id")
        )
        files = data.get("files", [])
        print(f"files {files}")
        for file in files:
            await MessageAttachment.create(
                message_id=message.id,
                file_url=file.get("url"),
                file_name=file.get("file_name"),
                file_type=file.get("file_type"),
                file_size=file.get("file_size"),
            )

    async def on_message_seen(self, sid, data):
        messageId = data.get("uuid")
        conversation_id = self.rooms.get(sid)
        if not conversation_id:
            return

        conversation = get_conversation(conversation_id)

        if not conversation:
            return
            
        for si in conversation["sids"]:
            if si == sid:
                continue

            await self.emit(
                self.message_seen,
                {"uui": messageId, "sid": sid},
                room=si,
            )

        await update_for_seen_db(messageId=messageId)

    async def on_typing(self, sid, data):
        """Handle typing events."""
        print(f"Typing event from {sid}: {data}")
        conversation_id = self.rooms.get(sid)
        if not conversation_id:
            return

        conversation = get_conversation(conversation_id)
        if not conversation:
            return

        for si in conversation["sids"]:
            if si == sid:
                continue

            await self.emit(
                self.receive_typing,
                {
                    "message": data.get("message"),
                    "sid": sid,
                    "mode": data.get("mode", "typing"),
                },
                room=si,
            )

    async def on_stop_typing(self, sid):
        """Handle stop typing events."""
        print(f"Stop typing event from {sid}")
        conversation_id = self.rooms.get(sid)
        if not conversation_id:
            return

        conversation = get_conversation(conversation_id)
        if not conversation:
            return

        for si in conversation["sids"]:
            if si == sid:
                continue
            print(f"Stopping typing for {si} from {sid}")
            await self.emit(
                self.stop_typing,
                {
                    "message": "",
                    "sid": sid,
                    "mode": "stop-typing",
                },
                room=si,
            )

    def on_disconnect(self, sid):
        conversation_id = self.rooms.get(sid)
        if conversation_id:
            conversation = get_conversation(conversation_id)
            if conversation:
                conversation["sids"].remove(sid)
                conversation["online"] = len(conversation["sids"]) > 0
                print(f"❌ Disconnected: {sid} (conversation_id: {conversation_id})")
