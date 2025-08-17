import logging
from datetime import datetime
from time import time

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from src.factory.notification import NotificationFactory
from src.modules.auth.models import User
from src.modules.ticket.enums import (
    TicketAlertTypeEnum,
    TicketLogActionEnum,
    WarningLevelEnum,
)
from src.modules.ticket.models import TicketSLA
from src.modules.ticket.models.priority import TicketPriority
from src.modules.ticket.models.ticket import Ticket, TicketAlert
from src.modules.ticket.schemas import (
    CreateSLASchema,
    EditTicketSLASchema,
    PriorityOut,
    SLAOut,
)
from src.modules.ticket.websocket.sla_websocket import AlertNameSpace
from src.socket_config import alert_ns, sio
from src.utils.common import extract_subset_from_dict
from src.utils.exceptions.ticket import TicketSLANotFound
from src.utils.get_templates import get_templates
from src.utils.response import CustomResponse as cr
from src.utils.validations import TenantEntityValidator

logger = logging.getLogger(__name__)


class TicketSLAServices:
    """
    Ticket SLA services methods
    """

    async def register_sla(self, payload: CreateSLASchema):
        """
        Registers the SLA to the organization
        """
        try:

            # we need to validate the priority doesn't belong to other organization
            tenant = TenantEntityValidator()
            await tenant.validate(TicketPriority, payload.priority_id)

            # create and logging
            sla = await TicketSLA.create(**payload.model_dump())
            await sla.save_to_log(action=TicketLogActionEnum.TICKET_SLA_CREATED)

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully registered the Service Level Agreement",
                data=sla.to_json(SLAOut),
            )
        except IntegrityError as e:
            logger.exception(e)
            return cr.error(
                message="Error while creating sla",
                data="SLA for this priority is already defined",
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"{e.detail if e.detail else str(e)}",
                data=str(e),
            )

    async def list_slas(self):
        """
        List all the SLA of the organization
        """
        try:
            sla_list = await TicketSLA.filter(
                related_items=[
                    selectinload(TicketSLA.priority),
                    selectinload(TicketSLA.tickets),
                ]
            )
            slas = [
                s.to_json(
                    schema=SLAOut,
                    include_relationships=True,
                    related_schemas={"priority": PriorityOut},
                )
                for s in sla_list
            ]

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully fetched all the sla",
                data=slas,
            )

        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"{e.detail if e.detail else str(e)}",
            )

    async def get_sla(self, sla_id: int):
        """
        Get sla by id
        """
        try:
            sla = await TicketSLA.find_one(where={"id": sla_id})

            if not sla:
                raise TicketSLANotFound(detail="Ticket SLA not found")

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully fetched the sla",
                data=sla.to_json(SLAOut),
            )

        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"{e.detail if e.detail else str(e)}",
                data=str(e),
            )

    async def edit_sla(self, sla_id: int, payload: EditTicketSLASchema):
        """
        Edits the sla if exists
        """
        try:

            sla = await TicketSLA.find_one(where={"id": sla_id})

            if not sla:
                raise TicketSLANotFound(detail="Ticket SLA not found")

            data = payload.model_dump(exclude_none=True)
            if not data:
                raise HTTPException(
                    detail="Nothing to update", status_code=HTTP_400_BAD_REQUEST
                )

            if "priority_id" in data:
                tenant = TenantEntityValidator()
                await tenant.validate(TicketPriority, data["priority_id"])

            # updating and logging
            await TicketSLA.update(sla_id, **data)
            await sla.save_to_log(
                action=TicketLogActionEnum.TICKET_SLA_UPDATED,
                previous_value=extract_subset_from_dict(sla.to_json(), data),
                new_value=data,
            )

            return cr.success(message="Successfully updated the ticket sla")
        except Exception as e:
            logger.exception(e)
            return cr.error(message=f"{e.detail if e.detail else str(e)}", data=str(e))

    async def delete_sla(self, sla_id: int):
        """
        Soft delete the sla
        """
        try:
            sla = await TicketSLA.find_one(where={"id": sla_id})
            if not sla:
                raise TicketSLANotFound()

            ticket_exists = await self.find_ticket_by_sla(sla)
            if ticket_exists:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Tickets with this sla exists, hence cannot be deleted",
                )

            await TicketSLA.delete(where={"id": sla_id})
            await sla.save_to_log(
                action=TicketLogActionEnum.TICKET_SLA_DELETED,
                previous_value=sla.to_json(),
            )
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully deleted the SLA",
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"{e.detail if e.detail else str(e)}",
                data=str(e),
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
        await self._check_breach("response", ticket, response_time, "response time")
        await self._check_breach(
            "resolution", ticket, resolution_time, "resolution time"
        )

    async def _check_breach(
        self, w_type: str, ticket: Ticket, time_percentage: int, time_label: str
    ):
        if time_percentage < WarningLevelEnum.WARNING_75:
            return

        breach_level = self.get_enum_from_range(time_percentage)

        if breach_level == WarningLevelEnum.WARNING_75:
            await self.handle_warning(
                w_type, ticket, breach_level, f"75% of the {time_label} has elapsed"
            )
        elif breach_level == WarningLevelEnum.WARNING_100:
            await self.handle_warning(
                w_type, ticket, breach_level, f"SLA {time_label} has been breached"
            )

    async def handle_warning(
        self, w_type: str, ticket: Ticket, level: WarningLevelEnum, message: str
    ):
        """
        Checks if warning already exists and sends alert and email if not
        """

        alert_type = (
            TicketAlertTypeEnum.RESPONSE.value
            if w_type == "response"
            else TicketAlertTypeEnum.RESOLUTION.value
        )

        alert_exists = await TicketAlert.find_one(
            where={
                "ticket_id": ticket.id,
                "alert_type": alert_type,
                "warning_level": level.value,
            }
        )

        if alert_exists:
            return

        await self.send_alert_broadcast(ticket, message)

        data = {
            "ticket_id": ticket.id,
            "alert_type": alert_type,
            "warning_level": level.value,
            "sent_at": datetime.utcnow(),
        }
        await TicketAlert.create(**data)
        await self._send_email(ticket, message)

    async def send_alert_broadcast(self, ticket: Ticket, message: str):
        """
        Responsible for sending alert message to all the broadcast via a socket
        """
        logger.info("Sending the broadcast")
        sc_user_ids = (
            alert_ns.user_ids
        )  # list of user_ids connected to the alertnamespace socket
        receiver_id = [assginee.id for assginee in ticket.assignees]
        receiver_id.append(ticket.created_by_id)
        logger.info("The receivers", receiver_id)
        for user_id in receiver_id:
            if user_id in sc_user_ids:
                await sio.emit(
                    "ticket_alert",
                    {"message": message},
                    namespace="/alert",
                    to=sc_user_ids[user_id],  # sid corresponding to the user id
                )

    async def _send_email(self, ticket: Ticket, message: str):
        """
        Sends SLA breach email to ticket assignees + creator.
        """
        receivers = [assignee.email for assignee in ticket.assignees]
        creator = await User.find_one(where={"id": ticket.created_by_id})
        if creator:
            receivers.append(creator.email)

        html_content = {"message": message, "ticket": ticket}
        template = await get_templates(
            name="ticket/sla-breach-email.html", content=html_content
        )

        logger.info(f"The receivers {receivers} {ticket.sender_domain}")
        receivers.append("rajipmahato68@gmail.com")
        for receiver in receivers:
            email = NotificationFactory.create("email")
            await email.send_ticket_email(
                subject="SLA breach",
                recipients=receiver,
                body_html=template,
                from_email=(ticket.sender_domain, ticket.organization.name),
                ticket=ticket,
                mail_type=TicketLogActionEnum.SLA_BREACH_EMAIL_SENT,
            )

    async def find_ticket_by_sla(self, sla: TicketSLA):
        """
        Finds the ticket by sla
        """
        try:
            tickets = await Ticket.filter(where={"priority_id": sla.priority_id})
            return tickets
        except Exception as e:
            return None


sla_service = TicketSLAServices()
