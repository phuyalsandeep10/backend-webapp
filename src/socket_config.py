import socketio

from src.app import app
from src.modules.chat.websocket import ChatNamespace
from src.modules.ticket.websocket.sla_websocket import AlertNameSpace

# Create the Socket.IO Async server (ASGI mode)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
socket_app = socketio.ASGIApp(
    socketio_server=sio, other_asgi_app=app, socketio_path="/ws/sockets/socket.io"
)


alert_ns = AlertNameSpace("/alert")

sio.register_namespace(ChatNamespace())
sio.register_namespace(alert_ns)
