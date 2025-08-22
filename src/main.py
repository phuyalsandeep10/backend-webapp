import logging

from fastapi import Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.app import app
from src.config.broadcast import broadcast
from src.routers import add_routers
from src.utils.exceptions import add_exceptions_handler
from src.socket_config import socket_app
from src.events import *


# custom exceptions
add_exceptions_handler(app)

# logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s -%(name)s - %(message)s"
)


# adding routers
add_routers(app)

templates = Jinja2Templates(directory="templates")


async def sender(websocket: WebSocket, room: str):
    async with broadcast.subscribe(channel=f"room_{room}") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


async def receiver(websocket: WebSocket, room: str):
    async for message in websocket.iter_text():
        await broadcast.publish(channel=f"room_{room}", message=message)


@app.get("/")
def read_root():
    return {"Hello": "Hello Chatboq World"}


@app.get("/chat")
async def get(request: Request):
    with open("src/templates/index.html") as f:
        return HTMLResponse(f.read())


@app.get("/health")
def read_items():
    return "Health check OK"

