from typing import List, Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator
from pydantic_core import PydanticCustomError

from src.modules.ticket.enums import PriorityEnum, TicketStatusEnum


class AssigneeOut(BaseModel):
    email: EmailStr
    name: str


class CreateTicketSchema(BaseModel):
    title: str
    description: str
    sender_domain: EmailStr
    notes: Optional[str] = None
    attachments: Optional[List[str]] = None
    priority_id: int
    department_id: int
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


class EditTicketSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sender_domain: Optional[str] = None
    notes: Optional[str] = None
    attachment: Optional[str] = None
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    department_id: Optional[str] = None
    sla_id: Optional[str] = None
    created_by_id: Optional[str] = None
    updated_by_id: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_location: Optional[str] = None
    assignees: Optional[List[int]] = None
    is_spam: Optional[List[int]] = None

    model_config = {"extra": "forbid"}


class CreatePrioriySchema(BaseModel):
    name: str
    level: int
    bg_color: str
    fg_color: str

    model_config = {"extra": "forbid"}


class EditTicketPrioritySchema(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    color: Optional[str] = None


class CreateTicketStatusSchema(BaseModel):
    name: str
    bg_color: str
    fg_color: str
    is_default: Optional[bool] = False
    status_category: TicketStatusEnum
    model_config = {"extra": "forbid"}


class EditTicketStatusSchema(BaseModel):
    name: Optional[str] = None
    is_default: Optional[bool] = None
    color: Optional[str] = None
    status_category: Optional[TicketStatusEnum] = None


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
    priority_id: int

    model_config = {"extra": "forbid"}


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

    sla: SLAOut
    contact: ContactOut
    assignees: AssigneeOut


class PriorityOut(CreatePrioriySchema):
    id: int


class TicketStatusOut(CreateTicketStatusSchema):
    id: int


class TicketAttachmentOut(BaseModel):
    attachment: List[str]
