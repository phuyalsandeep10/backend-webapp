from src.app import app
import socketio

# Create the Socket.IO Async server (ASGI mode)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
socket_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app,socketio_path="/ws/sockets/socket.io")

class ChatNamespace(socketio.AsyncNamespace):
    def __init__(self):
        super().__init__("/chat")

    async def on_connect(self, sid, environ, auth):
        print("✅ Connected to /chat:", sid)

    async def on_message(self, sid, data):
        print("💬 Message:", data)
        await self.emit("recieve-message", data, room=sid)

    def on_disconnect(self, sid):
        print("❌ Disconnected:", sid)

sio.register_namespace(ChatNamespace())