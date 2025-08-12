import logging
from typing import ClassVar, Optional, Union

import src.modules.ticket.models as TicketModel
from src.modules.ticket.enums import TicketLogActionEnum, TicketLogEntityEnum

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
        previous_value: Optional[Union[str, dict]] = None,
        new_value: Optional[Union[str, dict]] = None,
    ):
        try:

            if not self.entity_type:
                raise ValueError(f"{self.__class__.__name__} must define entity_type")

            ticket_id = None
            if self.entity_type == TicketLogEntityEnum.TICKET:
                ticket_id = self.id

            data = {
                "ticket_id": ticket_id,
                "entity_type": self.entity_type,
                "action": action,
                "description": description,
                "previous_value": previous_value,
                "new_value": new_value,
            }
            await TicketModel.TicketLog.create(**data)
            logger.info(f"{self.entity_type.value}--{action.value}--save to log")
        except Exception as e:
            logger.exception(e)
