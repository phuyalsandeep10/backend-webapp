from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Column
from sqlmodel import Field, ForeignKey

from src.common.models import BaseModel
from src.modules.ticket.enums import TicketEmailTypeEnum


class TicketEmailLog(BaseModel, table=True):
    __tablename__ = "ticket_email_log"  # type:ignore

    ticket_id: int = Field(
        sa_column=Column(ForeignKey("tickets.id", ondelete="CASCADE"))
    )
    email_type: TicketEmailTypeEnum
    recipient: EmailStr
    sent_at: datetime = Field(default_factory=datetime.utcnow)
