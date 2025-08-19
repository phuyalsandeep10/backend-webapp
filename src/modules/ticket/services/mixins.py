import logging
from typing import ClassVar, Optional, Union

import src.modules.ticket.models as TicketModel
from src.modules.ticket.enums import TicketLogActionEnum, TicketLogEntityEnum
from src.modules.ticket.schemas import TicketLogSchema

logger = logging.getLogger(__name__)


class LoggingMixin:
    """
    Provides save_in_log functionality for all inheriting models
    """

    entity_type: ClassVar[TicketLogEntityEnum]

    async def save_to_log(
        self,
        action: TicketLogActionEnum,
        description: Optional[str] = None,
        ticket_id: Optional[int] = None,
        previous_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
    ):
        try:

            if not self.entity_type:
                raise ValueError(f"{self.__class__.__name__} must define entity_type")

            if self.entity_type == TicketLogEntityEnum.TICKET and ticket_id is None:
                ticket_id = self.id

            organization_id = None
            if ticket_id:
                ticket = await TicketModel.Ticket.find_one(where={"id": ticket_id})
                if not ticket:
                    return
                organization_id = ticket.organization_id

            data = TicketLogSchema(
                organization_id=organization_id,
                ticket_id=ticket_id,
                entity_type=self.entity_type,
                action=action,
                description=description,
                previous_value=previous_value,
                new_value=new_value,
            )
            await TicketModel.TicketLog.create(**data.model_dump(exclude_none=True))
            logger.info(f"{self.entity_type.value}--{action.value}--save to log")
        except Exception as e:
            logger.exception(e)
