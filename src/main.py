from typing import Union

from fastapi import FastAPI
from src.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware
from src.modules.auth.router import router as auth_router
from src.modules.organizations.router import router as organization_router
from src.modules.admin.router import router as admin_router
from src.modules.team.router import router as team_router
from src.modules.chat.routers.customer import router as customer_router
from src.modules.chat.routers.conversation import router as conversation_router
from src.app import app
from fastapi.responses import HTMLResponse
from fastapi import Request
from src.modules.chat.websocket import route
from src.config.broadcast import broadcast

from fastapi import WebSocket, WebSocketDisconnect, Query, HTTPException, status


# ...existing code...
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(organization_router, prefix="/organizations", tags=["organizations"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(team_router, prefix="/teams", tags=["teams"])
app.include_router(customer_router, prefix="/customers", tags=["customers"])
app.include_router(conversation_router, prefix="/conversations", tags=["conversations"])

# ...existing code...


async def sender(websocket: WebSocket, room: str):
    async with broadcast.subscribe(channel=f"room_{room}") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


async def receiver(websocket: WebSocket, room: str):
    async for message in websocket.iter_text():
        await broadcast.publish(channel=f"room_{room}", message=message)


@app.websocket("/{room}")
async def websocket_chat(websocket: WebSocket, room: str):
    await websocket.accept()
    await run_until_first_complete(
        (receiver, {"websocket": websocket, "room": room}),
        (sender, {"websocket": websocket, "room": room}),
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/chat")
async def get(request: Request):
    with open("src/templates/index.html") as f:
        return HTMLResponse(f.read())


@app.get("/health")
def read_items():
    return "Health check OK"
