import logging
import sys

from sqlalchemy.orm import selectinload

from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.services.sla import sla_service
from src.modules.ticket.services.status import ticket_status_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)  # print to stdout
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


async def check_sla_breach():
    """
    Checks the sla breach of every tickets
    """
    # listing all tickets whose organization is not none
    all_tickets = await Ticket.filter_without_tenant()

    if not all_tickets:
        logger.info("No tickets")
        return
    # getting the default ticket status with close_status set by organization
    closed_ticket_status = await ticket_status_service.get_all_status_category_by_name(
        name="closed"
    )
    tickets = await Ticket.filter_without_tenant(
        where={"status_id": {"ne": closed_ticket_status.id}, "opened_at": {"ne": None}},
        related_items=[
            selectinload(Ticket.sla),
            selectinload(Ticket.assignees),
            selectinload(Ticket.organization),
        ],
    )
    for ticket in tickets:
        if not ticket.opened_at:
            return
        response_remaining_time = sla_service.calculate_sla_response_time_percentage(
            ticket.sla.response_time, int(ticket.opened_at.timestamp())
        )
        resolution_remaining_time = (
            sla_service.calculate_sla_resolution_time_percentage(
                ticket.sla.resolution_time, int(ticket.opened_at.timestamp())
            )
        )
        logger.error(f"Response time {response_remaining_time}")
        logger.error(f"Resolution time {resolution_remaining_time}")
        await sla_service.sla_breach_notification(
            ticket, response_remaining_time, resolution_remaining_time
        )
