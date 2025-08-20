import asyncio
import logging
from typing import ClassVar, List

from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey
from sqlmodel import Field

import src.modules.ticket.services.mixins as Mixin
from src.common.models import TenantModel
from src.modules.ticket.enums import TicketLogEntityEnum, TicketMessageDirectionEnum

logger = logging.getLogger(__name__)


class TicketMessage(TenantModel, Mixin.LoggingMixin, table=True):
    """Ticket Message table"""

    __tablename__ = "ticket_messages"
    entity_type: ClassVar[TicketLogEntityEnum] = TicketLogEntityEnum.TICKET_MESSAGE

    ticket_id: int = Field(
        sa_column=Column(ForeignKey("org_tickets.id", ondelete="CASCADE"))
    )
    sender: EmailStr = Field(nullable=False)
    receiver: EmailStr = Field(nullable=False)
    direction: str
    content: str
    attachments: str = Field(nullable=True)
