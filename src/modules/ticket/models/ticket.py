from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr, ValidationError, model_validator
from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, PrimaryKeyConstraint, Relationship

from src.common.models import BaseModel, CommonModel
from src.modules.chat.models.customer import Customer
from src.modules.ticket.enums import TicketAlertTypeEnum, WarningLevelEnum

if TYPE_CHECKING:
    from src.modules.auth.models import User
    from src.modules.organizations.models import Organization
    from src.modules.team.models import Team
    from src.modules.ticket.models import TicketSLA
    from src.modules.ticket.models.priority import TicketPriority
    from src.modules.ticket.models.status import TicketStatus


class TicketAssigneesLink(BaseModel, table=True):
    __tablename__ = "ticket_assignees"  # type: ignore

    ticket_id: int = Field(
        sa_column=Column(ForeignKey("org_tickets.id", ondelete="CASCADE"))
    )
    assignee_id: int = Field(
        sa_column=Column(ForeignKey("sys_users.id", ondelete="SET NULL"))
    )


class TicketAlert(BaseModel, table=True):
    __tablename__ = "ticket_alerts"  # type:ignore

    ticket_id: int = Field(
        sa_column=Column(ForeignKey("org_tickets.id", ondelete="CASCADE"))
    )
    alert_type: TicketAlertTypeEnum
    warning_level: WarningLevelEnum
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    ticket: Optional["Ticket"] = Relationship(back_populates="alerts")


class Ticket(CommonModel, table=True):
    __tablename__ = "org_tickets"  # type:ignore

    title: str
    description: str
    attachment: Optional[str] = None
    organization_id: int = Field(
        sa_column=Column(ForeignKey("sys_organizations.id", ondelete="CASCADE"))
    )
    priority_id: int = Field(
        sa_column=Column(ForeignKey("ticket_priority.id", ondelete="SET NULL"))
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
    sla_id: int = Field(
        sa_column=Column(ForeignKey("ticket_sla.id", ondelete="SET NULL"))
    )
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
    sla: "TicketSLA" = Relationship(back_populates="tickets")
    customer: "Customer" = Relationship(back_populates="tickets")
    priority: "TicketPriority" = Relationship(back_populates="tickets")
    status: "TicketStatus" = Relationship(back_populates="tickets")
    assignees: List["User"] = Relationship(
        back_populates="assigned_tickets", link_model=TicketAssigneesLink
    )
    alerts: List["TicketAlert"] = Relationship(
        back_populates="ticket",
    )
    organization: "Organization" = Relationship(back_populates="tickets")
    department: "Team" = Relationship(back_populates="tickets")
    # issued: "User" = Relationship(back_populates="tickets")

    def to_dict(self):
        payload = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "attachment": self.attachment,
            "priority": self.priority.to_dict(),
            "status": self.status.to_dict(),
            "sla": self.sla.to_dict(),
            "department": self.department.to_dict(),
            # "issued": self.issued.to_dict(),
            "assignees": [assignee.to_dict() for assignee in self.assignees],
            "created_at": self.created_at.isoformat(),
            "is_spam": self.is_spam,
        }
        if self.customer_id is None:
            payload["customer_name"] = (self.customer_name,)
            payload["customer_email"] = (self.customer_email,)
            payload["customer_phone"] = (self.customer_phone,)
            payload["customer_location"] = (self.customer_location,)
        else:
            payload["customer"] = self.customer.to_dict()

        return payload

    def __str__(self):
        return self.title
