import logging
from datetime import datetime
from time import time

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_403_FORBIDDEN

from src.modules.auth.models import User
from src.modules.ticket.enums import WarningLevelEnum
from src.modules.ticket.models import TicketSLA
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import CreateSLASchema, SLAOut
from src.utils.response import CustomResponse as cr

logger = logging.getLogger(__name__)


class TicketSLAServices:
    """
    Ticket SLA services methods
    """

    async def register_sla(self, payload: CreateSLASchema, user: User):
        """
        Registers the SLA to the organization
        """
        try:

            sla = await TicketSLA.create(**payload.model_dump())
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully registered the Service Level Agreement",
                data=sla.to_json(SLAOut),
            )
        except IntegrityError as e:
            logger.exception(e)
            return cr.error(
                message="Error while creating sla",
            )
        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while registering Service Level Agreement",
            )

    async def list_slas(self, user):
        """
        List all the SLA of the organization
        """
        try:
            sla_list = await TicketSLA.filter()
            slas = [s.to_json(SLAOut) for s in sla_list]

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully fetched all the sla",
                data=slas,
            )

        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while fetching Service Level Agreement",
            )

    async def get_sla(self, sla_id: int):
        """
        Get sla by id
        """
        try:
            sla = await TicketSLA.find_one(where={"id": sla_id})

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully fetched the sla",
                data=sla.to_json(SLAOut),
            )

        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while fetching Service Level Agreement",
            )

    async def delete_sla(self, sla_id: int):
        """
        Soft delete the sla
        """
        try:
            await TicketSLA.delete(where={"id": sla_id})
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully deleted the SLA",
            )
        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while deleting the SLA",
            )

    def calculate_sla_response_time_percentage(
        self, response_time: int, opened_at: int
    ) -> int:
        """
        Opened at time must be sent in timestamp format in terms of second
        """
        due_time = opened_at + response_time
        percentage = ((due_time - int(time())) * 100) / due_time
        logger.info(f"The due_time {due_time}")
        logger.info(f"The opened_at {opened_at}")
        logger.info(f"The now {int(time())}")
        logger.info(f"The percentage {percentage}")

        return int(percentage)

    def calculate_sla_resolution_time_percentage(
        self, resolution_time: int, opened_at: int
    ) -> int:
        """
        Opened at time must be sent in timestamp format in terms of second
        """
        due_time = opened_at + resolution_time
        percentage = ((due_time - int(time())) * 100) / due_time

        return int(percentage)

    def get_enum_from_range(self, value: int) -> WarningLevelEnum:
        if 75 <= value < 90:
            return WarningLevelEnum.WARNING_75
        elif 90 <= value < 100:
            return WarningLevelEnum.WARNING_90
        elif value >= 100:
            return WarningLevelEnum.WARNING_100
        else:
            raise ValueError("Value is below the minimum range")

    async def sla_breach_notification(self, ticket, response_time, resolution_time):
        """
        IT will send the notification if there is any sla breach
        """
        pass

    async def sla_response_breach_notification(
        self, ticket, response_time, resolution_time
    ):
        is_response_time_breached = await self.check_response_time_breach(response_time)
        if not is_response_time_breached:
            return  # because we don't need to look at resolution time if even is_response_time is not breached yet
        await self.handle_sla_response_breach(response_time)

    async def handle_sla_response_breach(self, response_time):
        response_breach = self.get_enum_from_range(response_time)
        if response_breach is WarningLevelEnum.WARNING_75:
            logger.info("Response time reached 75")
        if response_breach is WarningLevelEnum.WARNING_100:
            logger.info("Response time reached 100")

    async def check_response_time_breach(self, response_time: int) -> bool:
        """
        Returns True if response_time has passed over 75%
        """
        if response_time < WarningLevelEnum.WARNING_75:
            return False
        return True


sla_service = TicketSLAServices()
