import logging

from celery import shared_task
from redis.asyncio import Redis


logger = logging.getLogger(__name__)

r = Redis()


@shared_task
def check_sla_percentage():
    """
    Check the sla percentage from the sla services, check_ticket_sla_status
    after that if the percentage is 75% then send a warning and set the ticket_alert value so that we
    can know later that it has been sent
    for websocket first publish to redis then redish sends data or message to the websocket
    also maybe sending email is also a fall back for socket

    """
    r.publish("sla_channel", "Checking the sla percentage")
