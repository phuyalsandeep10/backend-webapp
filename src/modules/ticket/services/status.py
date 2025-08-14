import logging
from typing import List

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from src.modules.ticket.enums import TicketLogActionEnum
from src.modules.ticket.models import TicketStatus
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import (
    CreateTicketStatusSchema,
    EditTicketStatusSchema,
    TicketStatusOut,
)
from src.utils.common import extract_subset_from_dict
from src.utils.exceptions.ticket import TicketStatusNotFound
from src.utils.response import CustomResponse as cr

logger = logging.getLogger(__name__)


class TicketStatusService:

    async def list_ticket_status(self, user):
        """
        List all the ticket status on the basis of the organization
        """
        try:
            ticket_status = await TicketStatus.filter()
            payload = [status.to_json(TicketStatusOut) for status in ticket_status]
            return cr.success(message="Successfully listed status", data=payload)
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while listing status")

    async def create_ticket_status(self, payload: List[CreateTicketStatusSchema], user):
        """
        create single status or list of ticket status at the same time
        """
        try:
            for d in payload:
                data = d.model_dump()
                record = await TicketStatus.find_one(where={"name": data["name"]})
                if not record:
                    # creating ticket status and saving to log
                    status = await TicketStatus.create(**data)
                    await status.save_to_log(action=TicketLogActionEnum.STATUS_CREATED)

            return cr.success(
                message="Successfully created ticket status", status_code=201
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while creating ticket status")

    async def get_ticket_status(self, ticket_status_id: int, user):
        """
        List particular ticket status of the organization
        """
        try:
            ticket_status = await TicketStatus.find_one(where={"id": ticket_status_id})
            if ticket_status is None:
                return cr.error(message="Not found")
            return cr.success(
                message="Successfully listed ticket status",
                data=ticket_status.to_json(TicketStatusOut) if ticket_status else None,
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while listing ticket status")

    async def delete_ticket_status(self, ticket_status_id: int, user):
        """
        Delete ticket status by id
        """
        try:
            status = await TicketStatus.find_one(where={"id": ticket_status_id})
            if not status:
                raise TicketStatusNotFound()

            # checking if tickets has been created with that ticket_stauts
            ticket_exists = await self.find_ticket_by_status(ticket_status_id)
            if ticket_exists:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Tickets with this status exists, hence cannot be deleted",
                )

            # deleting and logging
            await TicketStatus.delete(where={"id": ticket_status_id})
            await status.save_to_log(
                action=TicketLogActionEnum.STATUS_DELETED,
                previous_value=status.to_json(),
            )
            return cr.success(message="Successfully deleted the ticket status")
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while deleting the ticket status")

    async def edit_ticket_status(
        self, ticket_status_id: int, payload: EditTicketStatusSchema, user
    ):
        """
        Edit ticket status of the organization
        """
        try:
            ticket_status = await TicketStatus.find_one(
                where={
                    "id": ticket_status_id,
                }
            )
            if not ticket_status:
                raise TicketStatusNotFound()

            # updating and logging
            updated_ticket_status = await TicketStatus.update(
                ticket_status.id, **payload.model_dump(exclude_none=True)
            )
            await ticket_status.save_to_log(
                action=TicketLogActionEnum.STATUS_UPDATED,
                previous_value=extract_subset_from_dict(
                    ticket_status.to_json(), payload.model_dump(exclude_none=True)
                ),
                new_value=payload.model_dump(exclude_none=True),
            )

            return cr.success(
                message="Successfully updated ticket status",
                data=(
                    updated_ticket_status.to_json(TicketStatusOut)
                    if updated_ticket_status
                    else None
                ),
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while editing ticket status", data=str(e))

    async def get_status_category_by_name(self, name: str):
        """
        Returns the default close category ticket status
        """
        ticket_status = await TicketStatus.find_one(where={"status_category": name})
        if not ticket_status:
            raise TicketStatusNotFound(
                f"No default ticket status has been set with {name} status category"
            )

        return ticket_status

    async def get_all_status_category_by_name(self, name: str):
        """
        Returns the default close category ticket status
        """
        ticket_status = await TicketStatus.find_one(
            where={"status_category": name, "organization_id": {"ne": None}}
        )
        if not ticket_status:
            raise TicketStatusNotFound(
                f"No default ticket status has been set with {name} status category"
            )

        return ticket_status

    async def find_ticket_by_status(self, status_id: int):
        """
        Returns the all tickets by that status
        """
        try:
            tickets = await Ticket.filter(where={"status_id": status_id})
            return tickets
        except Exception as e:
            return None


ticket_status_service = TicketStatusService()
