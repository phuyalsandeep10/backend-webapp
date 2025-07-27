from src.modules.auth.models import User
from src.modules.ticket.models import Priority
from src.utils.response import CustomResponse as cr


class PriorityService:

    async def list_priorities(self, user: User):
        """
        List all the priorites on the basis of the organization
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            priorities = await Priority.filter(
                where={"organization_id": organization_id}
            )
            return cr.success(message="Successfully listed priorities", data=priorities)
        except Exception as e:
            print(e)
            return cr.error(message="Error while listing priorities")

    async def create_priorities(self, payload, user):
        """
        List single priorites or list of priorities at the same time
        """
        try:
            organization_id: int = user.attributes.get("organization_id")
            for data in payload:
                record = await Priority.find_one(
                    where={"name": data.name, "organization_id": organization_id}
                )
                if not record:
                    data["organization_id"] = organization_id
                    await Priority.create(**dict(data))

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


priority_service = PriorityService()
