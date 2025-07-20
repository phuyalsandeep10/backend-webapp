from .app import app
import socketio

# Create the Socket.IO Async server (ASGI mode)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')



# ASGIApp wraps Socket.IO and FastAPI into one ASGI application
socket_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"data {data}")
    await sio.emit('response', {'data': 'Received: '}, room=sid)