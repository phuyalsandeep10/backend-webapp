from typing import List, Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator
from pydantic_core import PydanticCustomError

from src.modules.ticket.enums import PriorityEnum, StatusEnum


class AssigneeOut(BaseModel):
    email: EmailStr
    name: str


class CreateTicketSchema(BaseModel):
    title: str
    description: str
    attachment: Optional[str] = None
    priority_id: int
    status_id: int
    department_id: int
    sla_id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_location: Optional[str] = None
    assignees: Optional[List[int]] = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_customer_anonymousness(self):
        customer_id = self.customer_id
        customer_name = self.customer_name
        customer_email = self.customer_email
        customer_phone = self.customer_phone
        customer_location = self.customer_location

        result = [
            field
            for field in [
                customer_name,
                customer_email,
                customer_phone,
                customer_location,
            ]
        ]

        if customer_id is None and any(res is None for res in result):
            raise PydanticCustomError(
                "missing_customer_info",
                "Either provide customer_id or anonymous customer information (name/email/phone/location)",
            )
        return self


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
