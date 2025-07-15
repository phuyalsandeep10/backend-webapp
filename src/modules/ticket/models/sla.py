from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship

from src.common.models import BaseModel

from .ticket import Ticket


class SLA(BaseModel, table=True):
    __tablename__: str = "sla"  # type: ignore

    name: str = Field(nullable=True)
    response_time: int = Field(nullable=False)
    resolution_time: int = Field(nullable=False)
    issued_by: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    tickets: List[Ticket] = Relationship(back_populates="sla")

    def __str__(self):
        return f"{self.name}-{self.created_at}"
