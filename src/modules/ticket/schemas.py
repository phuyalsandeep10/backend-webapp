from typing import List, Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr, Field, model_validator

from src.modules.ticket.enums import PriorityEnum, StatusEnum


class AssigneeOut(BaseModel):
    email: EmailStr
    name: str


class CreateTicketSchema(BaseModel):
    title: str
    description: str
    priority: PriorityEnum = PriorityEnum.MEDIUM
    status: StatusEnum = StatusEnum.OPEN
    sla_id: int
    contact_id: int
    assignees: Optional[List[int]] = None

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


class FullCreateTicketSchema(BaseModel):
    title: str
    description: str
    priority: PriorityEnum = PriorityEnum.MEDIUM
    status: StatusEnum = StatusEnum.OPEN
    sla_id: Optional[int] = None
    contact_id: Optional[int] = None
    sla: Optional[CreateSLASchema] = None
    contact: Optional[CreateContactSchema] = None
    assignees: Optional[List[int]] = None

    @model_validator(mode="after")
    def check_sla_fields(self):
        if self.sla_id is not None and self.sla is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either provide sla_id or sla details",
            )
        if self.sla_id is None and self.sla is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Atleast provide sla_id or sla details",
            )
        return self

    @model_validator(mode="after")
    def check_contact_fields(self):
        if self.contact_id is not None and self.contact is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either provide contact_id or contact details",
            )
        if self.contact_id is None and self.contact is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Atleast provide contact_id or contact details",
            )
        return self


class ContactOut(CreateContactSchema):
    id: int


class SLAOut(CreateSLASchema):
    id: int
    issued_by: int
    created_at: str


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    priority: PriorityEnum = PriorityEnum.MEDIUM
    status: StatusEnum = StatusEnum.OPEN

    sla: SLAOut
    contact: ContactOut
    assignees: AssigneeOut
