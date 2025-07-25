from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr, ValidationError, model_validator
from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, PrimaryKeyConstraint, Relationship

from src.common.models import BaseModel
from src.modules.chat.models.customer import Customer
from src.modules.ticket.enums import TicketAlertTypeEnum, WarningLevelEnum

if TYPE_CHECKING:
    from src.modules.auth.models import User
    from src.modules.organizations.models import Organization
    from src.modules.team.models import Team
    from src.modules.ticket.models import SLA, Contact
    from src.modules.ticket.models.priority import Priority
    from src.modules.ticket.models.status import TicketStatus


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
    attachment: Optional[str] = None
    organization_id: int = Field(
        sa_column=Column(ForeignKey("sys_organizations.id", ondelete="CASCADE"))
    )
    priority_id: int = Field(
        sa_column=Column(ForeignKey("priority.id", ondelete="SET NULL"))
    )
    status_id: int = Field(
        sa_column=Column(ForeignKey("ticket_status.id", ondelete="SET NULL"))
    )
    department_id: int = Field(
        sa_column=Column(ForeignKey("org_teams.id", ondelete="SET NULL"))
    )
    issued_by: int = Field(
        sa_column=Column(ForeignKey("sys_users.id", ondelete="SET NULL"))
    )
    sla_id: int = Field(sa_column=Column(ForeignKey("sla.id", ondelete="SET NULL")))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    customer_id: int = Field(
        sa_column=Column(
            ForeignKey("org_customers.id", ondelete="SET NULL"), nullable=True
        )
    )
    is_spam: bool = Field(default=False)
    customer_name: str = Field(nullable=True)
    customer_email: EmailStr = Field(nullable=True)
    customer_phone: str = Field(nullable=True)
    customer_location: str = Field(nullable=True)

    # Relationships
    sla: "SLA" = Relationship(back_populates="tickets")
    customer: "Customer" = Relationship(back_populates="tickets")
    priority: "Priority" = Relationship(back_populates="tickets")
    status: "TicketStatus" = Relationship(back_populates="tickets")
    assignees: List["User"] = Relationship(
        back_populates="assigned_tickets", link_model=TicketAssigneesLink
    )
    alerts: List["TicketAlert"] = Relationship(
        back_populates="ticket",
    )
    organization: List["Organization"] = Relationship(back_populates="tickets")
    department: List["Team"] = Relationship(back_populates="tickets")
    issued: List["User"] = Relationship(back_populates="tickets")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority_id,
            "status": self.status_id,
            "sla": self.sla.to_dict(),
            "customer": self.customer.to_dict(),
            "assignees": [assignee.to_dict() for assignee in self.assignees],
        }

    def __str__(self):
        return self.title
