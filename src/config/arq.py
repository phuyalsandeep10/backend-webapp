from arq import cron
from arq.connections import RedisSettings

from src.tasks import send_email  # the function above


class WorkerSettings:
    functions = [send_email]
    redis_settings = RedisSettings(host="localhost", port=6379, database=0)
