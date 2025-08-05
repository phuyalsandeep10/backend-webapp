from broadcaster import Broadcast
from src.config.settings import settings

broadcast = Broadcast(settings.CELEREY_BROKER_URL)
