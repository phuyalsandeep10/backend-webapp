from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship

from src.common.models import BaseModel
from src.modules.ticket.enums import PriorityEnum, StatusEnum

if TYPE_CHECKING:
    from src.modules.ticket.models import SLA, Contact


class Ticket(BaseModel, table=True):
    __tablename__ = "tickets"  # type:ignore

    title: str
    description: str
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    status: StatusEnum = Field(default=StatusEnum.OPEN)
    # assignees: List[User] = Relationship(back_populates="User")
    issued_by: int = Field(nullable=False)
    sla_id: int = Field(sa_column=Column(ForeignKey("sla.id", ondelete="SET NULL")))
    contact_id: int = Field(
        sa_column=Column(ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    )
    sla: "SLA" = Relationship(back_populates="tickets")
    contacts: "Contact" = Relationship(back_populates="tickets")

    def __str__(self):
        return self.title
