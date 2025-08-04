from typing import List

from sqlalchemy import Column
from sqlmodel import BigInteger, Field, Relationship

from src.common.models import TenantModel

from .ticket import Ticket


class TicketSLA(TenantModel, table=True):
    """
    Ticket SLA model
    """

    __tablename__: str = "ticket_sla"  # type: ignore

    name: str = Field(nullable=True, unique=True)
    response_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    resolution_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    tickets: List[Ticket] = Relationship(back_populates="sla", passive_deletes=True)

    def __str__(self):
        return f"{self.name}-{self.created_at}"
