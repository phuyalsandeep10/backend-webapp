from typing import List

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from src.common.models import BaseModel
from src.modules.ticket.models.ticket import Ticket


class Contact(BaseModel, table=True):
    __tablename__ = "contacts"  # type:ignore

    email: EmailStr = Field(nullable=False, unique=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    phone: str = Field(nullable=False, max_digits=10)

    tickets: List[Ticket] = Relationship(back_populates="contacts")

    def __str__(self):
        return f"{self.email}"
