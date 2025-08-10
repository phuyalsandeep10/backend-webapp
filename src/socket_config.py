from src.app import app
import socketio
from src.websocket.chat_handler import ChatNamespace, redis_listener
from src.config.settings import settings


# Create the Socket.IO Async server (ASGI mode)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
socket_app = socketio.ASGIApp(
    socketio_server=sio, other_asgi_app=app, socketio_path="/ws/sockets/socket.io"
)


# async def create_socketio_server():
#     # Use AsyncRedisManager so server can scale horizontally
#     mgr = socketio.AsyncRedisManager(settings.REDIS_URL)

#     sio = socketio.AsyncServer(
#         async_mode="asgi",
#         client_manager=mgr,
#         cors_allowed_origins=settings.CORS_ORIGINS,
#         logger=False,
#         engineio_logger=False,
#     )

#     # register namespaces
#     sio.register_namespace(ChatNamespace("/chat"))

#     return sio


sio.register_namespace(ChatNamespace())


# Wire redis subscriber at app startup to avoid circular imports in chat_handler
@app.on_event("startup")
async def start_ws_redis_listener():
    import asyncio

    asyncio.create_task(redis_listener(sio))
