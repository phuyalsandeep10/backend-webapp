from typing import TYPE_CHECKING, List

from sqlalchemy import Column
from sqlmodel import Field, ForeignKey, Relationship, UniqueConstraint

from src.common.models import BaseModel, CommonModel

if TYPE_CHECKING:
    from src.modules.organizations.models import Organization
    from src.modules.ticket.models.ticket import Ticket


class TicketPriority(CommonModel, table=True):
    __tablename__ = "ticket_priority"  # type:ignore
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uniq_org_name"),
    )

    name: str
    level: int
    color: str
    organization_id: int = Field(
        sa_column=Column(ForeignKey("sys_organizations.id", ondelete="CASCADE"))
    )
    tickets: List["Ticket"] = Relationship(back_populates="priority")
    organizations: List["Organization"] = Relationship(back_populates="priorities")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "color": self.color,
        }
