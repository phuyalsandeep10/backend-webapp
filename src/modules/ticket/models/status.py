from typing import TYPE_CHECKING, ClassVar, List

from sqlmodel import Relationship, UniqueConstraint

import src.modules.ticket.services.mixins as Mixin
from src.common.models import TenantModel
from src.modules.ticket.enums import TicketLogEntityEnum

if TYPE_CHECKING:
    from src.modules.organizations.models import Organization
    from src.modules.ticket.models.ticket import Ticket


class TicketStatus(TenantModel, Mixin.LoggingMixin, table=True):
    """
    Ticket Status model
    """

    __tablename__ = "ticket_status"  # type:ignore
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uniq_org_ticket_status_name"),
    )
    entity_type: ClassVar[TicketLogEntityEnum] = TicketLogEntityEnum.TICKET_STATUS

    name: str
    bg_color: str
    fg_color: str
    status_category: str
    tickets: List["Ticket"] = Relationship(back_populates="status")
    organizations: List["Organization"] = Relationship(back_populates="ticket_status")

    def __str__(self):
        return f"{self.name}-{self.organization_id}"
