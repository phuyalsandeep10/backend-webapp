from typing import List

from kombu import message

from src.modules.auth.models import User
from src.modules.ticket.models import TicketStatus
from src.modules.ticket.schemas import CreateTicketStatusSchema
from src.utils.response import CustomResponse as cr


class TicketStatusService:

    async def list_ticket_status(self, user):
        """
        List all the ticket status on the basis of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            ticket_status = await TicketStatus.filter(
                where={"organization_id": organization_id}
            )
            payload = [status.to_dict() for status in ticket_status]
            return cr.success(message="Successfully listed status", data=payload)
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
                    dict_data = dict(data)
                    dict_data["organization_id"] = organization_id
                    await TicketStatus.create(**dict_data)

            return cr.success(
                message="Successfully created ticket status", status_code=201
            )
        except Exception as e:
            print(e)
            return cr.error(message="Error while creating ticket status")

    async def get_ticket_status(self, ticket_status_id: int, user):
        """
        List particular ticket status of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            ticket_status = await TicketStatus.find_one(
                where={"organization_id": organization_id, "id": ticket_status_id}
            )
            if ticket_status is None:
                return cr.error(message="Not found")
            return cr.success(
                message="Successfully listed ticket status",
                data=ticket_status.to_dict() if ticket_status else None,
            )
        except Exception as e:
            print(e)
            return cr.error(message="Error while listing ticket status")

    async def delete_ticket_status(self, ticket_status_id: int, user):
        """
        Delete ticket status by id
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            await TicketStatus.delete(
                where={"organization_id": organization_id, "id": ticket_status_id}
            )
            return cr.success(message="Successfully deleted the ticket status")
        except Exception as e:
            print(e)
            return cr.error(message="Error while deleting the ticket status")


ticket_status_service = TicketStatusService()
