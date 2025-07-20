from redis.asyncio import Redis

from src.modules.ticket.routers.sla import broadcast


async def start_listener():
    r = Redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("sla_channel")

    async for msg in pubsub.listen():
        await broadcast(msg["data"])
