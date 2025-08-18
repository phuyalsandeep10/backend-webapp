import socketio
from src.websocket.chat_namespaces.customer_chat_namespace import CustomerChatNamespace
from src.websocket.chat_namespaces.agent_chat_namespace import AgentChatNamespace
from src.config.redis.redis_listener import redis_listener
from src.config.settings import settings
from socketio import AsyncRedisManager

# ✅ Correct: Initialize once
redis_url = settings.REDIS_URL
mgr = AsyncRedisManager(redis_url)


from src.app import app
from src.modules.chat.websocket import ChatNamespace
from src.modules.ticket.websocket.sla_websocket import AlertNameSpace

# Create the Socket.IO Async server (ASGI mode)
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    client_manager=mgr,
)


# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
socket_app = socketio.ASGIApp(
    socketio_server=sio, other_asgi_app=app, socketio_path="/ws/sockets/socket.io"
)


sio.register_namespace(CustomerChatNamespace())
sio.register_namespace(AgentChatNamespace())


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

            traceback.print_exception(
                type(task.exception()), task.exception(), task.exception().__traceback__
            )
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

alert_ns = AlertNameSpace("/alert")
sio.register_namespace(alert_ns)