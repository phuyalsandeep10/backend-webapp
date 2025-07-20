from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, PrimaryKeyConstraint, Relationship

from src.common.models import BaseModel
from src.modules.ticket.enums import (
    PriorityEnum,
    StatusEnum,
    TicketAlertTypeEnum,
    WarningLevelEnum,
)

if TYPE_CHECKING:
    from src.modules.auth.models import User
    from src.modules.ticket.models import SLA, Contact


class TicketAssigneesLink(BaseModel, table=True):
    __tablename__ = "ticket_assignees"  # type: ignore

    ticket_id: int = Field(
        sa_column=Column(ForeignKey("tickets.id", ondelete="CASCADE"))
    )
    assignee_id: int = Field(
        sa_column=Column(ForeignKey("sys_users.id", ondelete="SET NULL"))
    )
    __table_args__ = (PrimaryKeyConstraint("ticket_id", "assignee_id"),)


class TicketAlert(BaseModel, table=True):
    __tablename__ = "ticket_alerts"  # type:ignore

    ticket_id: int = Field(
        sa_column=Column(ForeignKey("tickets.id", ondelete="CASCADE"))
    )
    alert_type: TicketAlertTypeEnum
    warning_level: WarningLevelEnum
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    ticket: Optional["Ticket"] = Relationship(back_populates="alerts")


class Ticket(BaseModel, table=True):
    __tablename__ = "tickets"  # type:ignore

    title: str
    description: str
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    status: StatusEnum = Field(default=StatusEnum.OPEN)
    issued_by: int = Field(nullable=False)
    sla_id: int = Field(sa_column=Column(ForeignKey("sla.id", ondelete="SET NULL")))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    contact_id: int = Field(
        sa_column=Column(ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    )
    sla: "SLA" = Relationship(back_populates="tickets")
    contacts: "Contact" = Relationship(back_populates="tickets")
    assignees: List["User"] = Relationship(
        back_populates="assigned_tickets", link_model=TicketAssigneesLink
    )
    alerts: List["TicketAlert"] = Relationship(
        back_populates="ticket",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "sla": self.sla.to_dict(),
            "contact": self.contacts.to_dict(),
            "assignees": [assignee.to_dict() for assignee in self.assignees],
        }

    def __str__(self):
        return self.title
