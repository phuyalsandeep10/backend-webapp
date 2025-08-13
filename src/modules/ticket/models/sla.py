from typing import TYPE_CHECKING, ClassVar, List

from sqlalchemy import Column
from sqlmodel import BigInteger, Field, ForeignKey, Relationship, UniqueConstraint

import src.modules.ticket.services.mixins as Mixin
from src.common.models import TenantModel
from src.modules.ticket.enums import TicketLogEntityEnum

if TYPE_CHECKING:

    from src.modules.ticket.models.priority import TicketPriority

from .ticket import Ticket


class TicketSLA(TenantModel, Mixin.LoggingMixin, table=True):
    """
    Ticket SLA model
    """

    __tablename__: str = "ticket_sla"  # type: ignore
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            "priority_id",
            name="uniq_org_ticket_sla_name_level",
        ),
        UniqueConstraint(
            "organization_id",
            "priority_id",
            name="uniq_org_ticket_sla_level",
        ),
    )
    entity_type: ClassVar[TicketLogEntityEnum] = TicketLogEntityEnum.TICKET_SLA

    name: str = Field(nullable=True, unique=True)
    response_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    resolution_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    priority_id: int = Field(
        sa_column=(
            Column(
                ForeignKey("ticket_priority.id", ondelete="SET NULL"), nullable=False
            )
        )
    )
    is_default: bool = Field(default=False)
    tickets: List[Ticket] = Relationship(back_populates="sla", passive_deletes=True)
    priority: "TicketPriority" = Relationship(back_populates="sla")

    def __str__(self):
        return f"{self.name}-{self.created_at}"
