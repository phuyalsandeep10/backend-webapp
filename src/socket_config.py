from src.app import app
import socketio
from src.modules.chat.websocket import ChatNamespace

# Create the Socket.IO Async server (ASGI mode)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
socket_app = socketio.ASGIApp(
    socketio_server=sio, other_asgi_app=app, socketio_path="/ws/sockets/socket.io"
)



sio.register_namespace(ChatNamespace())
