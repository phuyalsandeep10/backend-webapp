import logging

from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

from src.modules.ticket.models import TicketPriority
from src.modules.ticket.schemas import EditTicketPrioritySchema, PriorityOut
from src.utils.exceptions.ticket import TicketPriorityExists
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

                await TicketPriority.create(**data)

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
            await TicketPriority.delete(where={"id": priority_id})
            return cr.success(message="Successfully deleted priority", data=None)
        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while deleting priority", data=str(e))

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

            updated_priority = await TicketPriority.update(
                priority.id, **payload.model_dump(exclude_none=True)
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


priority_service = TicketPriorityService()
