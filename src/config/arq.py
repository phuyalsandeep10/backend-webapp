from arq import cron
from arq.connections import RedisSettings

from src.tasks.ticket_task import broadcast_ticket_message, send_ticket_task_email


class WorkerSettings:
    functions = [send_ticket_task_email, broadcast_ticket_message]
    redis_settings = RedisSettings(host="localhost", port=6379, database=0)
