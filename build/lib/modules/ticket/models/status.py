from typing import TYPE_CHECKING, List

from sqlalchemy import Column
from sqlmodel import Field, ForeignKey, Relationship, UniqueConstraint

from src.common.models import CommonModel

if TYPE_CHECKING:
    from src.modules.organizations.models import Organization
    from src.modules.ticket.models.ticket import Ticket


class TicketStatus(CommonModel, table=True):
    __tablename__ = "ticket_status"  # type:ignore
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uniq_org_status_name"),
    )

    name: str
    bg_color: str
    fg_color: str
    is_default: bool = Field(default=False)
    organization_id: int = Field(
        sa_column=Column(
            ForeignKey("sys_organizations.id", ondelete="CASCADE"), nullable=True
        )
    )
    status_category: str
    tickets: List["Ticket"] = Relationship(back_populates="status")
    organizations: List["Organization"] = Relationship(back_populates="ticket_status")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
        }
