from typing import List

from src.modules.auth.models import User
from src.modules.ticket.models import Priority, TicketStatus
from src.modules.ticket.schemas import CreateTicketStatusSchema
from src.utils.response import CustomResponse as cr


class TicketStatusService:

    async def list_ticket_status(self, user: User):
        """
        List all the ticket status on the basis of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            ticket_status = await TicketStatus.filter(
                where={"organization_id": organization_id}
            )
            return cr.success(message="Successfully listed status", data=ticket_status)
        except Exception as e:
            print(e)
            return cr.error(message="Error while listing status")

    async def create_ticket_status(self, payload: List[CreateTicketStatusSchema], user):
        """
        create single status or list of ticket status at the same time
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            for data in payload:
                record = await TicketStatus.find_one(
                    where={"name": data.name, "organization_id": organization_id}
                )
                if not record:
                    data["organization_id"] = organization_id
                    await TicketStatus.create(**dict(data))

            return cr.success(
                message="Successfully created priorities", status_code=201
            )
        except Exception as e:
            print(e)
            return cr.error(message="Error while creating priorities")

    async def get_priority(self, priority_id: int, user: User):
        """
        List particular priority of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            priority = await Priority.find_one(
                where={"organization_id": organization_id, "id": priority_id}
            )
            return cr.success(message="Successfully listed priority", data=priority)
        except Exception as e:
            print(e)
            return cr.error(message="Error while listing priority")


ticket_service = TicketStatusService()
