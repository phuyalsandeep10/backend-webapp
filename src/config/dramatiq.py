import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.asyncio import AsyncIO

from src.config.settings import settings

broker = RedisBroker(url=settings.REDIS_URL)
broker.add_middleware(AsyncIO())
dramatiq.set_broker(broker)
