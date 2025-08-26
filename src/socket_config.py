import socketio
from socketio import AsyncRedisManager
from socketio.redis_manager import redis

from src.config.redis.redis_listener import  redis_listener
from src.config.settings import settings
from src.websocket.chat_namespaces.agent_chat_namespace import AgentChatNamespace
from src.websocket.chat_namespaces.customer_chat_namespace import CustomerChatNamespace
from src.websocket.namespace.ticket.ticket_namespace import TicketNameSpace

# ✅ Correct: Initialize once
try:
    redis_url = settings.REDIS_URL
    mgr = AsyncRedisManager(redis_url)
    print("✅ Redis manager created successfully")
except Exception as e:
    print(f"⚠️ Error creating Redis manager: {e}")
    import traceback
    traceback.print_exc()
    raise


from src.app import app

# Initialize ticket namespace variables at module level
alert_ns = None
ticket_ns = None

try:
    from src.modules.ticket.websocket.sla_websocket import AlertNameSpace
    from src.websocket.namespace.ticket.ticket_namespace import TicketNameSpace
    print("✅ Ticket WebSocket modules imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import ticket WebSocket modules: {e}")
    AlertNameSpace = None
    TicketNameSpace = None

# Create the Socket.IO Async server (ASGI mode)
try:
    sio = socketio.AsyncServer(
        async_mode="asgi",
        cors_allowed_origins="*",
        client_manager=mgr,
    )
    print("✅ Socket.IO server created successfully")
except Exception as e:
    print(f"⚠️ Error creating Socket.IO server: {e}")
    import traceback
    traceback.print_exc()
    raise


# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
try:
    socket_app = socketio.ASGIApp(
        socketio_server=sio, other_asgi_app=app, socketio_path="/ws/sockets/socket.io"
    )
    print("✅ ASGI app created successfully")
except Exception as e:
    print(f"⚠️ Error creating ASGI app: {e}")
    import traceback
    traceback.print_exc()
    # Fallback to basic ASGI app
    socket_app = app


try:
    sio.register_namespace(CustomerChatNamespace())
    sio.register_namespace(AgentChatNamespace())
    print("✅ Chat namespaces registered successfully")
except Exception as e:
    print(f"⚠️ Error registering chat namespaces: {e}")
    import traceback
    traceback.print_exc()

# Register ticket namespaces if available
if AlertNameSpace and TicketNameSpace:
    try:
        alert_ns = AlertNameSpace("/alert")
        ticket_ns = TicketNameSpace("/tickets", sio)
        sio.register_namespace(alert_ns)
        sio.register_namespace(ticket_ns)
        print("✅ Ticket namespaces registered successfully")
    except Exception as e:
        print(f"⚠️ Error registering ticket namespaces: {e}")
        import traceback
        traceback.print_exc()
        # Set to None if registration fails
        alert_ns = None
        ticket_ns = None
else:
    print("⚠️ Skipping ticket namespace registration - modules not available")
    # Variables are already set to None above

# Global task reference to prevent garbage collection
redis_listener_task = None


# Wire redis subscriber at app startup to avoid circular imports in chat_handler
@app.on_event("startup")
async def start_ws_redis_listener():
    import asyncio

    global redis_listener_task

    print("🚀 Starting WebSocket Redis listener...")
    try:
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
    except Exception as e:
        print(f"❌ Failed to start Redis listener: {e}")
        import traceback
        traceback.print_exc()


@app.on_event("shutdown")
async def stop_ws_redis_listener():
    import asyncio

    global redis_listener_task
    if redis_listener_task and not redis_listener_task.done():
        print("🛑 Stopping Redis listener task...")
        try:
            redis_listener_task.cancel()
            await redis_listener_task
        except asyncio.CancelledError:
            print("✅ Redis listener task cancelled")
        except Exception as e:
            print(f"⚠️ Error stopping Redis listener: {e}")
            import traceback
            traceback.print_exc()
