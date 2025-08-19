import logging

from socketio import AsyncServer

from ..base import BaseNameSpace

logger = logging.getLogger(__name__)


class TicketNameSpace(BaseNameSpace):

    async def on_connect(self, sid, environ, auth):
        print("Connecting")
        result = await super().on_connect(sid, environ, auth)
        if result is False:
            return False

        # subscribing to our ticket channel
        # await self.subscribe("tickets")

    async def on_join_ticket(self, sid, data):
        """
        Join a ticket room
        """
        session = await self.get_session(sid, self.namespace)
        user = session.get("user")
        ticket_id = data["ticket_id"]
        if not ticket_id:
            return

        room = f"ticket_{ticket_id}"
        logger.info(f"User {user.email} has joined {room}")
        await self.join_room(sid, room)
        # subscribing to the room channel
        # await self.redis_subscribe(room)

    async def broadcast_message(self, message: str, user_email: str, ticket_id: int):
        if not ticket_id or not user_email or not message:
            return

        room = f"ticket_{ticket_id}"

        payload = {"user": user_email, "room": room, "message": message}
        await self.redis_publish(channel=room, message=payload)

        await self.sio.emit(
            "on_broadcast", room=room, namespace=self.namespace, data=payload
        )
        logger.info(f"User {user_email} sent message in {room} : {message}")
