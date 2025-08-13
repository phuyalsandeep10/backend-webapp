import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_409_CONFLICT

from src.modules.ticket.enums import TicketLogActionEnum
from src.modules.ticket.models import TicketPriority
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import EditTicketPrioritySchema, PriorityOut
from src.utils.common import extract_subset_from_dict
from src.utils.exceptions.ticket import TicketPriorityExists, TicketPriorityNotFound
from src.utils.response import CustomResponse as cr

logger = logging.getLogger(__name__)


class TicketPriorityService:

    async def list_priorities(self, user):
        """
        List all the priorites on the basis of the organization
        """
        try:

            priorities = await TicketPriority.filter()
            payload = [priority.to_json(PriorityOut) for priority in priorities]
            return cr.success(message="Successfully listed priorities", data=payload)
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while listing priorities", data=str(e))

    async def create_priorities(self, payload, user):
        """
        create single priority or list of priorities at the same time
        """
        try:
            for d in payload:
                data = d.model_dump()
                record = await TicketPriority.find_one(
                    where={
                        "name": {"mode": "insensitive", "value": data["name"]},
                        "level": data["level"],
                    }
                )
                if record:
                    raise TicketPriorityExists(
                        detail="Ticket priority with this name or level already exists"
                    )

                # saving and logging
                priority = await TicketPriority.create(**data)
                await priority.save_to_log(
                    action=TicketLogActionEnum.PRIORITY_CREATED,
                    new_value=priority.to_json(),
                )

            return cr.success(
                message="Successfully created priorities", status_code=201
            )
        except IntegrityError as e:
            logger.exception(e)
            return cr.error(
                message="Priority with this name or level already exists",
                status_code=HTTP_409_CONFLICT,
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while creating priorities", data=str(e))

    async def get_priority(self, priority_id: int, user):
        """
        List particular priority of the organization
        """
        try:
            priority = await TicketPriority.find_one(where={"id": priority_id})
            if priority is None:
                return cr.error(message="Not found")
            return cr.success(
                message="Successfully listed priority",
                data=priority.to_json(PriorityOut) if priority else None,
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while listing priority")

    async def delete_priority(self, priority_id: int, user):
        """
        soft delete particular priority of the organization
        """
        try:
            # checking if priority exists
            priority = await TicketPriority.find_one(where={"id": priority_id})
            if not priority:
                raise TicketPriorityNotFound()
            # before deleting finding if there is any tickets with this priority
            ticket_exists = await self.find_ticket_by_priority(priority_id)
            if ticket_exists:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Tickets with this priority exists, hence cannot be deleted",
                )
            # deleting and logging
            await TicketPriority.delete(where={"id": priority_id})
            await priority.save_to_log(
                action=TicketLogActionEnum.PRIORITY_DELETED,
                previous_value=priority.to_json(),
            )

            return cr.success(message="Successfully deleted priority", data=None)
        except Exception as e:
            logger.exception(e)
            return cr.error(
                message=f"Error while deleting priority,{str(e)}", data=str(e)
            )

    async def edit_priority(
        self, priority_id: int, payload: EditTicketPrioritySchema, user
    ):
        """
        Edit priority of the organization
        """
        try:
            priority = await TicketPriority.find_one(
                where={
                    "id": priority_id,
                }
            )
            if priority is None:
                return cr.error(
                    message="Priority not found", status_code=HTTP_400_BAD_REQUEST
                )

            # updating and logging
            updated_priority = await TicketPriority.update(
                priority.id, **payload.model_dump(exclude_none=True)
            )
            await priority.save_to_log(
                action=TicketLogActionEnum.PRIORITY_UPDATED,
                previous_value=extract_subset_from_dict(
                    priority.to_json(), payload.model_dump(exclude_none=True)
                ),
                new_value=payload.model_dump(exclude_none=True),
            )

            return cr.success(
                message="Successfully updated  prioirty",
                data=(
                    updated_priority.to_json(PriorityOut) if updated_priority else None
                ),
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while editing priority", data=str(e))

    async def find_ticket_by_priority(self, priority_id: int):
        """
        Returns the list of tickets by priority
        """
        try:
            tickets = await Ticket.filter(where={"priority_id": priority_id})
            return tickets
        except Exception as e:
            return None


priority_service = TicketPriorityService()
