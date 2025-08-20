from arq import cron
from arq.connections import RedisSettings

from src.tasks.ticket_task import send_ticket_task_email


class WorkerSettings:
    functions = [send_ticket_task_email]
    redis_settings = RedisSettings(host="localhost", port=6379, database=0)
