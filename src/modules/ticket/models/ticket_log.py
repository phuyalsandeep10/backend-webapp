from typing import Optional

from sqlmodel import JSON, Column, Field, ForeignKey

from src.common.models import TenantModel


class TicketLog(TenantModel, table=True):
    """
    The model to audit logs of ticket
    """

    __tablename__ = "org_tickets_logs"  # type:ignore

    ticket_id: int = Field(
        sa_column=Column(
            ForeignKey("org_tickets.id", ondelete="SET NULL"), nullable=True
        )
    )
    entity_type: str = Field(nullable=False)
    action: str = Field(nullable=False)
    description: str = Field(nullable=True)
    previous_value: Optional[dict] = Field(sa_column=Column(JSON), default=None)
    new_value: Optional[dict] = Field(sa_column=Column(JSON), default=None)

    def __str__(self):
        return self.action
