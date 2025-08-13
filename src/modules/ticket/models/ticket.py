from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, List, Optional

from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship

import src.modules.ticket.services.mixins as Mixin
from src.common.models import BaseModel, CommonModel, TenantModel
from src.modules.ticket.enums import (
    TicketAlertTypeEnum,
    TicketLogEntityEnum,
    WarningLevelEnum,
)
from src.modules.ticket.schemas import (
    PriorityOut,
    SLAOut,
    TicketAttachmentOut,
    TicketStatusOut,
)

if TYPE_CHECKING:
    from src.modules.auth.models import User
    from src.modules.chat.models.customer import Customer
    from src.modules.organizations.models import Organization
    from src.modules.team.models import Team
    from src.modules.ticket.models import TicketSLA
    from src.modules.ticket.models.priority import TicketPriority
    from src.modules.ticket.models.status import TicketStatus


class TicketAttachment(CommonModel, table=True):
    """
    To store ticket attachments
    """

    __tablename__ = "ticket_attachments"  # type:ignore

    ticket_id: int = Field(
        sa_column=Column(ForeignKey("org_tickets.id", ondelete="CASCADE"))
    )
    attachment: str
    ticket: Optional["Ticket"] = Relationship(back_populates="attachments")


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
    alert_type: str
    warning_level: int
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    ticket: Optional["Ticket"] = Relationship(back_populates="alerts")


class Ticket(TenantModel, Mixin.LoggingMixin, table=True):
    """
    Ticket model
    """

    __tablename__ = "org_tickets"  # type:ignore
    entity_type: ClassVar[TicketLogEntityEnum] = TicketLogEntityEnum.TICKET

    title: str
    description: str
    sender_domain: EmailStr
    notes: Optional[str] = None
    priority_id: int = Field(
        sa_column=Column(ForeignKey("ticket_priority.id", ondelete="SET NULL"))
    )
    status_id: int = Field(
        sa_column=Column(ForeignKey("ticket_status.id", ondelete="SET NULL"))
    )
    department_id: int = Field(
        sa_column=Column(ForeignKey("org_teams.id", ondelete="SET NULL"))
    )
    sla_id: int = Field(
        sa_column=Column(ForeignKey("ticket_sla.id", ondelete="SET NULL"))
    )
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
    confirmation_token: Optional[str] = None
    opened_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Relationships
    sla: "TicketSLA" = Relationship(back_populates="tickets")
    customer: "Customer" = Relationship(back_populates="tickets")
    priority: "TicketPriority" = Relationship(back_populates="tickets")
    status: "TicketStatus" = Relationship(back_populates="tickets")
    assignees: List["User"] = Relationship(
        back_populates="assigned_tickets", link_model=TicketAssigneesLink
    )
    attachments: List["TicketAttachment"] = Relationship(back_populates="ticket")
    alerts: List["TicketAlert"] = Relationship(
        back_populates="ticket",
    )
    organization: "Organization" = Relationship(back_populates="tickets")
    department: "Team" = Relationship(back_populates="tickets")
    created_by: "User" = Relationship(
        back_populates="tickets",
        sa_relationship_kwargs={"foreign_keys": "[Ticket.created_by_id]"},
    )

    def to_dict(self):
        """
        Returns model value in dict
        """
        payload = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "attachment": [
                attachment.to_json(TicketAttachmentOut)
                for attachment in self.attachments
            ],
            "priority": self.priority.to_json(PriorityOut) if self.priority else None,
            "status": self.status.to_json(TicketStatusOut) if self.status else None,
            "sla": self.sla.to_json(SLAOut) if self.sla else None,
            "department": self.department.to_json() if self.department else None,
            "created_by": self.created_by.to_dict() if self.created_by else None,
            "assignees": [assignee.to_json() for assignee in self.assignees],
            "created_at": self.created_at.isoformat(),
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "is_spam": self.is_spam,
        }
        if self.customer_id is None:
            payload["customer_name"] = self.customer_name
            payload["customer_email"] = self.customer_email
            payload["customer_phone"] = self.customer_phone
            payload["customer_location"] = self.customer_location
        else:
            payload["customer"] = self.customer.to_json()

        return payload

    def __str__(self):
        return self.title
