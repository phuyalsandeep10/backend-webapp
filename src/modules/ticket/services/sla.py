import logging
from datetime import datetime
from time import time

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_403_FORBIDDEN

from src.factory.notification import NotificationFactory
from src.modules.auth.models import User
from src.modules.ticket.enums import TicketAlertTypeEnum, WarningLevelEnum
from src.modules.ticket.models import TicketSLA
from src.modules.ticket.models.ticket import Ticket, TicketAlert
from src.modules.ticket.schemas import CreateSLASchema, SLAOut
from src.modules.ticket.websocket.sla_websocket import AlertNameSpace
from src.socket_config import alert_ns, sio
from src.utils.get_templates import get_templates
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
        percentage = (current_time - opened_at) * 100 / (due_time - opened_at)
        """
        due_time = opened_at + response_time
        current_time = int(datetime.utcnow().timestamp())
        logger.info(f"Current response time {current_time}")
        logger.info(f"Due response time {due_time}")

        if current_time >= due_time:
            return 100

        percentage = ((current_time - opened_at) * 100) / (due_time - opened_at)

        return int(percentage)

    def calculate_sla_resolution_time_percentage(
        self, resolution_time: int, opened_at: int
    ) -> int:
        """
        Opened at time must be sent in timestamp format in terms of second
        """
        due_time = opened_at + resolution_time
        current_time = int(datetime.utcnow().timestamp())
        logger.info(f"Current resolution time {current_time}")
        logger.info(f"Due resolution time {due_time}")

        if current_time > due_time:
            return 100

        percentage = ((current_time - opened_at) * 100) / (due_time - opened_at)

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
        It will send the notification if there is any sla breach
        """
        await self.sla_response_breach_notification(ticket, response_time)
        await self.sla_resolution_breach_notification(ticket, resolution_time)

    async def sla_response_breach_notification(self, ticket, response_time):
        """
        Responsible for handling sla response time breach
        """
        if response_time < WarningLevelEnum.WARNING_75:
            return None

        response_breach = self.get_enum_from_range(response_time)
        if response_breach is WarningLevelEnum.WARNING_75:
            await self.handle_warning_75(
                w_type="response",
                ticket=ticket,
                message="75% of the response time has elapsed",
            )
        if response_breach is WarningLevelEnum.WARNING_100:
            await self.handle_warning_100(
                w_type="response",
                ticket=ticket,
                message="SLA Response time has been breached",
            )

    async def sla_resolution_breach_notification(self, ticket, resolution_time):
        """
        Responsible for handling sla resolution time breach
        """
        if resolution_time < WarningLevelEnum.WARNING_75:
            return None

        resolution_breach = self.get_enum_from_range(resolution_time)
        if resolution_breach is WarningLevelEnum.WARNING_75:
            await self.handle_warning_75(
                w_type="resolution",
                ticket=ticket,
                message="75% of the resolution time has elapsed",
            )
        if resolution_breach is WarningLevelEnum.WARNING_100:
            await self.handle_warning_100(
                w_type="resolution", ticket=ticket, message="SLA has been breached"
            )

    async def handle_warning_75(self, w_type: str, ticket: Ticket, message: str):
        """
        Handles when SLA time has elapsed 75%
        first it checks if the warning was already sent
        if none then it sends another one
        """
        alert = await TicketAlert.find_one(
            where={
                "ticket_id": ticket.id,
                "alert_type": (
                    TicketAlertTypeEnum.RESPONSE.value
                    if w_type == "response"
                    else TicketAlertTypeEnum.RESOLUTION.value
                ),
                "warning_level": WarningLevelEnum.WARNING_75.value,
            }
        )
        if not alert:
            await self.send_alert_broadcast(ticket, message)
            # saving in the ticketalert table
            data = {
                "ticket_id": ticket.id,
                "alert_type": (
                    TicketAlertTypeEnum.RESPONSE.value
                    if w_type == "response"
                    else TicketAlertTypeEnum.RESOLUTION.value
                ),
                "warning_level": WarningLevelEnum.WARNING_75.value,
                "sent_at": datetime.utcnow(),
            }
            await TicketAlert.create(**data)

            # sending mail
            receivers = [assginee.email for assginee in ticket.assignees]

            # getting email of the creator
            creater = await User.find_one(where={"id": ticket.created_by_id})

            if not creater:
                return

            receivers.append(creater.email)
            html_content = {"message": message, "ticket": ticket}
            template = await get_templates(
                name="ticket/sla-breach-email.html", content=html_content
            )

            email = NotificationFactory.create("email")
            email.send(subject="SLA breach", recipients=receivers, body_html=template)

    async def handle_warning_100(self, w_type: str, ticket: Ticket, message: str):
        """
        Handles when SLA time has elapsed 100%
        """
        alert = await TicketAlert.find_one(
            where={
                "ticket_id": ticket.id,
                "alert_type": (
                    TicketAlertTypeEnum.RESPONSE.value
                    if w_type == "response"
                    else TicketAlertTypeEnum.RESOLUTION.value
                ),
                "warning_level": WarningLevelEnum.WARNING_100.value,
            }
        )
        if not alert:
            await self.send_alert_broadcast(ticket, message)
            # saving in the ticketalert table
            data = {
                "ticket_id": ticket.id,
                "alert_type": (
                    TicketAlertTypeEnum.RESPONSE.value
                    if w_type == "response"
                    else TicketAlertTypeEnum.RESOLUTION.value
                ),
                "warning_level": WarningLevelEnum.WARNING_100.value,
                "sent_at": datetime.utcnow(),
            }
            await TicketAlert.create(**data)
            receivers = [assginee.email for assginee in ticket.assignees]

            # getting email of the creator
            creater = await User.find_one(where={"id": ticket.created_by_id})

            if not creater:
                return

            receivers.append(creater.email)
            html_content = {"message": message, "ticket": ticket}
            template = await get_templates(
                name="ticket/sla-breach-email.html", content=html_content
            )

            email = NotificationFactory.create("email")
            email.send(subject="SLA breach", recipients=receivers, body_html=template)

    async def send_alert_broadcast(self, ticket: Ticket, message: str):
        """
        Responsible for sending alert message to all the broadcast via a socket
        """
        sc_user_ids = (
            alert_ns.user_ids
        )  # list of user_ids connected to the alertnamespace socket
        receiver_id = [assginee.id for assginee in ticket.assignees]
        receiver_id.append(ticket.created_by_id)
        for user_id in receiver_id:
            if user_id in sc_user_ids:
                await sio.emit(
                    "ticket_alert",
                    {"message": message},
                    namespace="/alert",
                    to=sc_user_ids[user_id],  # sid corresponding to the user id
                )


sla_service = TicketSLAServices()
