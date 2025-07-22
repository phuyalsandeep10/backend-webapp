from src.app import app
import socketio

from src.modules.chat.models import conversation

# Create the Socket.IO Async server (ASGI mode)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
socket_app = socketio.ASGIApp(
    socketio_server=sio, other_asgi_app=app, socketio_path="/ws/sockets/socket.io"
)

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


class ChatNamespace(socketio.AsyncNamespace):
    def __init__(self):
        super().__init__("/chat")
        self.rooms = {}

    async def on_connect(self, sid, environ, auth):
        token = auth.get("token")
        customer_id = auth.get("customer_id")
        conversation_id = auth.get("conversation_id")

        if not customer_id or not conversation_id:
            return False

        conversation = get_conversation(conversation_id)

        if not conversation:
            conversation = create_conversation(conversation_id, customer_id)

        self.rooms[sid] = conversation_id
        conversation["sids"].append(sid)
        conversation["online"] = True

        print(f"✅ Connected to /chat: {sid} (conversation_id: {conversation_id})")
        return True

    async def on_message(self, sid, data):
        conversation_id = self.rooms.get(sid)
        if not conversation_id:
            return

        conversation = get_conversation(conversation_id)

        print(f"conversation id {conversation_id} and conversation {conversation}")

        if not conversation:
            return

        for si in conversation["sids"]:
            if si == sid:
                continue
            await self.emit(
                "recieve-message",
                {
                    "message": data.get("message"),
                    "sid": sid,
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


sio.register_namespace(ChatNamespace())
