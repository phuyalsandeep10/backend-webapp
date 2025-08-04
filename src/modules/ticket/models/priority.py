from typing import TYPE_CHECKING, List

from sqlmodel import Relationship, UniqueConstraint

from src.common.models import TenantModel

if TYPE_CHECKING:
    from src.modules.organizations.models import Organization
    from src.modules.ticket.models.ticket import Ticket


class TicketPriority(TenantModel, table=True):
    """
    Ticket Priority model
    """

    __tablename__ = "ticket_priority"  # type:ignore
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            "level",
            name="uniq_org_ticket_priority_name_level",
        ),
    )
    name: str
    level: int
    bg_color: str
    fg_color: str
    tickets: List["Ticket"] = Relationship(back_populates="priority")
    organization: "Organization" = Relationship(back_populates="ticket_priorities")

    def __str__(self):
        return f"{self.name}-{self.organization_id}"
