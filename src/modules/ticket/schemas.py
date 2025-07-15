from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.modules.ticket.enums.enums import PriorityEnum, StatusEnum


class CreateTicketSchema(BaseModel):
    title: str
    description: str
    priority: PriorityEnum = PriorityEnum.MEDIUM
    status: StatusEnum = StatusEnum.OPEN
    issued_by: int
    sla_id: int
    contact_id: int

    model_config = {"extra": "forbid"}


class CreateContactSchema(BaseModel):

    email: EmailStr
    first_name: str
    last_name: str
    phone: str

    model_config = {"extra": "forbid"}


class CreateSLASchema(BaseModel):

    name: str
    response_time: int
    resolution_time: int

    model_config = {"extra": "forbid"}
