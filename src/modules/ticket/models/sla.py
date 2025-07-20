from datetime import datetime
from typing import List

from sqlalchemy import Column
from sqlmodel import BigInteger, Field, Relationship

from src.common.models import BaseModel

from .ticket import Ticket


class SLA(BaseModel, table=True):
    __tablename__: str = "sla"  # type: ignore

    name: str = Field(nullable=True, unique=True)
    response_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    resolution_time: int = Field(sa_column=Column(BigInteger, nullable=False))
    issued_by: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    tickets: List[Ticket] = Relationship(back_populates="sla", passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "response_time": self.response_time,
            "resolution_time": self.resolution_time,
            "issued_by": self.issued_by,
            "created_at": self.created_at.isoformat(),
        }

    def __str__(self):
        return f"{self.name}-{self.created_at}"
