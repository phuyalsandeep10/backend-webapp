import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.asyncio import AsyncIO

broker = RedisBroker(url="redis://localhost:6379/0")
broker.add_middleware(AsyncIO())
dramatiq.set_broker(broker)
