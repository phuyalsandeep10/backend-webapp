from typing import List

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship

from src.common.models import BaseModel
from src.modules.auth.models import User
from src.modules.ticket.enums import PriorityEnum, StatusEnum


class Ticket(BaseModel, table=True):
    __tablename__ = "tickets"

    title: str
    description: str
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    status: StatusEnum = Field(default=StatusEnum.OPEN)
    assignees: List[User] = Relationship(back_populates="User")
    issued_by: int = Field(nullable=False)
    sla_id: int = Field(
        sa_column=Column(ForeignKey("sla.id", ondelete="CASCADE"), nullable=False)
    )
    sla: "SLA" = Relationship(back_populates="tickets")

    def __str__(self):
        return self.title
