from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, UniqueConstraint

from src.common.models import TenantModel

if TYPE_CHECKING:
    from src.modules.organizations.models import Organization
    from src.modules.ticket.models.ticket import Ticket


class TicketStatus(TenantModel, table=True):
    """
    Ticket Status model
    """

    __tablename__ = "ticket_status"  # type:ignore
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uniq_org_ticket_status_name"),
    )

    name: str
    bg_color: str
    fg_color: str
    is_default: bool = Field(default=False)
    status_category: str
    tickets: List["Ticket"] = Relationship(back_populates="status")
    organizations: List["Organization"] = Relationship(back_populates="ticket_status")

    def to_dict(self):
        """
        Returns the model value in dict
        """
        return {
            "id": self.id,
            "name": self.name,
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
        }

    def __str__(self):
        return f"{self.name}-{self.organization_id}"
