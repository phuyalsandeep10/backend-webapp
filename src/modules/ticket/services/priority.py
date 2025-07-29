from kombu import message
from starlette.status import HTTP_400_BAD_REQUEST

from src.modules.ticket.models import TicketPriority
from src.modules.ticket.schemas import EditTicketPrioritySchema
from src.utils.response import CustomResponse as cr


class TicketPriorityService:

    async def list_priorities(self, user):
        """
        List all the priorites on the basis of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            priorities = await TicketPriority.filter(
                where={"organization_id": organization_id}
            )

            payload = [priority.to_dict() for priority in priorities]
            return cr.success(message="Successfully listed priorities", data=payload)
        except Exception as e:
            print(e)
            return cr.error(message="Error while listing priorities")

    async def create_priorities(self, payload, user):
        """
        create single priority or list of priorities at the same time
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            for data in payload:
                record = await TicketPriority.find_one(
                    where={"name": data.name, "organization_id": organization_id}
                )
                if not record:
                    data["organization_id"] = organization_id
                    await TicketPriority.create(**dict(data))

            return cr.success(
                message="Successfully created priorities", status_code=201
            )
        except Exception as e:
            print(e)
            return cr.error(message="Error while creating priorities")

    async def get_priority(self, priority_id: int, user):
        """
        List particular priority of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            priority = await TicketPriority.find_one(
                where={"organization_id": organization_id, "id": priority_id}
            )
            if priority is None:
                return cr.error(message="Not found")
            return cr.success(
                message="Successfully listed priority",
                data=priority.to_dict() if priority else None,
            )
        except Exception as e:
            print(e)
            return cr.error(message="Error while listing priority")

    async def delete_priority(self, priority_id: int, user):
        """
        soft delete particular priority of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            await TicketPriority.delete(
                where={"organization_id": organization_id, "id": priority_id}
            )
            return cr.success(message="Successfully deleted priority", data=None)
        except Exception as e:
            print(e)
            return cr.error(message="Error while deleting priority")

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
                    "organization_id": user.attributes.get("organization_id"),
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
                data=(updated_priority.to_dict() if updated_priority else None),
            )
        except Exception as e:
            print(e)
            return cr.error(message="Error while editing priority", data=str(e))


priority_service = TicketPriorityService()
