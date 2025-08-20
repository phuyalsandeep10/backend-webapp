from typing import List

from sqlalchemy import Column, ForeignKey
from sqlmodel import BigInteger, Field, Relationship

from src.common.models import CommonModel

from .ticket import Ticket


class TicketSLA(CommonModel, table=True):
    __tablename__: str = "ticket_sla"  # type: ignore

    name: str = Field(nullable=True, unique=True)
    response_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    resolution_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    organization_id: int = Field(
        sa_column=Column(ForeignKey("sys_organizations.id", ondelete="CASCADE"))
    )
    is_default: bool = Field(default=False, nullable=False)
    issued_by: int = Field(nullable=False)
    tickets: List[Ticket] = Relationship(back_populates="sla", passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "response_time": self.response_time,
            "resolution_time": self.resolution_time,
            "issued_by": self.issued_by,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
        }

    def __str__(self):
        return f"{self.name}-{self.created_at}"
