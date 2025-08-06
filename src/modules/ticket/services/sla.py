import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_403_FORBIDDEN

from src.modules.auth.models import User
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
        self, response_time: int, created_at: datetime
    ) -> int:
        percentage = ((response_time - created_at.timestamp()) * 100) / response_time

        return int(percentage)

    def calculate_sla_resolution_time_percentage(
        self, resolution_time: int, created_at: datetime
    ) -> int:
        percentage = (
            resolution_time - (created_at.timestamp()) * 100
        ) / resolution_time

        return int(percentage)

    def check_ticket_sla_status(self, ticket: Ticket):
        response_time = self.calculate_sla_response_time_percentage(
            ticket.sla.response_time, ticket.created_at
        )
        resolution_time = self.calculate_sla_resolution_time_percentage(
            ticket.sla.resolution_time, ticket.created_at
        )

        return response_time, resolution_time


sla_service = TicketSLAServices()
