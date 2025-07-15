from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status
from typing import Dict, Set

app = FastAPI()


class Room:
    def __init__(self):
        self.customers: Set[WebSocket] = set()
        self.staff: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, role: str):
        await websocket.accept()
        if role == "agent":
            self.customers.add(websocket)

        else:
            self.staff.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.customers.discard(websocket)
        self.staff.discard(websocket)

    async def broadcast(self, sender_role: str, message: str):

        targets = self.staff if sender_role == "agent" else self.customers

        for conn in set(targets):
            try:
                await conn.send_text(message)
            except:
                targets.discard(conn)


rooms: Dict[str, Room] = {}
