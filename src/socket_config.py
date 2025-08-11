from src.app import app
import socketio
from src.websocket.chat_handler import ChatNamespace
from src.config.redis.redis_listener import redis_listener 
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


# Global task reference to prevent garbage collection
redis_listener_task = None

# Wire redis subscriber at app startup to avoid circular imports in chat_handler
@app.on_event("startup")
async def start_ws_redis_listener():
    import asyncio
    global redis_listener_task
    
    print("🚀 Starting WebSocket Redis listener...")
    
    # Create task with proper error handling
    redis_listener_task = asyncio.create_task(redis_listener(sio))
    
    # Add error callback to catch silent failures
    def task_done_callback(task):
        if task.exception():
            print(f"❌ Redis listener task failed: {task.exception()}")
            import traceback
            traceback.print_exception(type(task.exception()), task.exception(), task.exception().__traceback__)
        else:
            print("ℹ️ Redis listener task completed normally")
    
    redis_listener_task.add_done_callback(task_done_callback)
    print("✅ WebSocket Redis listener task created")

@app.on_event("shutdown")
async def stop_ws_redis_listener():
    import asyncio
    global redis_listener_task
    if redis_listener_task and not redis_listener_task.done():
        print("🛑 Stopping Redis listener task...")
        redis_listener_task.cancel()
        try:
            await redis_listener_task
        except asyncio.CancelledError:
            print("✅ Redis listener task cancelled")
        except Exception as e:
            print(f"⚠️ Error stopping Redis listener: {e}")
