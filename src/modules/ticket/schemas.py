from datetime import datetime
from typing import List, Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator
from pydantic.functional_validators import field_validator
from pydantic_core import PydanticCustomError

from src.modules.ticket.enums import (
    PriorityEnum,
    TicketLogActionEnum,
    TicketLogEntityEnum,
    TicketStatusEnum,
)


class AssigneeOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    address: str
    country: str
    language: str
    image: str
    mobile: str


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

        # ensures either customer_id or [customer_name,customer_email,customer_phone] are provided
        if customer_id is None and any(res is None for res in result):
            raise PydanticCustomError(
                "missing_customer_info",
                "Either provide customer_id or anonymous customer information (name/email/phone/location)",
            )

        # ensures both customer_id or [customer_name,customer_email,customer_phone] are not provided
        if customer_id is not None and not any(res is not None for res in result):
            raise PydanticCustomError(
                "invalid_customer_info",
                "Either send customer id or other customer information but not both",
            )

        # ensures if customer id is not provided all other email ,name, phone numbers are provided
        if customer_id is None and not all(res is not None for res in result):
            raise PydanticCustomError(
                "invalid_customer_info",
                "All customer details should be provided",
            )

        return self


class EditTicketSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sender_domain: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[List[str]] = None
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
    is_spam: Optional[bool] = None

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
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None


class CreateTicketStatusSchema(BaseModel):
    name: str
    bg_color: str
    fg_color: str
    status_category: TicketStatusEnum
    model_config = {"extra": "forbid"}


class EditTicketStatusSchema(BaseModel):
    name: Optional[str] = None
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
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

    @model_validator(mode="after")
    def check_time_negative(self):
        if self.response_time is not None and self.response_time <= 0:
            raise PydanticCustomError(
                "Cannot be negative",
                "Response time cannot be negative",
            )
        if self.resolution_time is not None and self.resolution_time <= 0:
            raise PydanticCustomError(
                "Cannot be negative",
                "Resolution time cannot be negative",
            )
        return self


class ContactOut(CreateContactSchema):
    id: int


class PriorityOut(CreatePrioriySchema):
    id: int


class SLAOut(CreateSLASchema):
    id: int
    issued_by: int
    created_at: datetime
    priority: PriorityOut


class TicketOut(BaseModel):
    id: int
    title: str
    description: str

    sla: SLAOut
    contact: ContactOut
    assignees: AssigneeOut


class TicketStatusOut(CreateTicketStatusSchema):
    id: int


class TicketAttachmentOut(BaseModel):
    attachment: List[str]


class EditTicketSLASchema(BaseModel):
    name: Optional[str] = None
    response_time: Optional[int] = None
    resolution_time: Optional[int] = None
    priority_id: Optional[int] = None

    @model_validator(mode="after")
    def check_time_negative(self):
        if self.response_time is not None and self.response_time <= 0:
            raise PydanticCustomError(
                "Cannot be negative",
                "Response time cannot be negative",
            )
        if self.resolution_time is not None and self.resolution_time <= 0:
            raise PydanticCustomError(
                "Cannot be negative",
                "Resolution time cannot be negative",
            )
        return self


class TicketByStatusSchema(BaseModel):
    status_id: int

    model_config = {"extra": "forbid"}


class TicketLogSchema(BaseModel):
    organization_id: Optional[int] = None
    ticket_id: Optional[int] = None
    entity_type: TicketLogEntityEnum
    action: TicketLogActionEnum
    description: Optional[str] = None
    previous_value: Optional[dict] = None
    new_value: Optional[dict] = None


class CreateTicketMessageSchema(BaseModel):

    ticket_id: int
    receiver: EmailStr
    content: str

    @field_validator("content")
    def content_cannot_be_empty_string(cls, value):
        if value.strip() == "":
            raise PydanticCustomError(
                "invalid content",
                "Content cannot be empty string",
            )
        return value


class EditTicketMessageSchema(BaseModel):

    content: str

    @field_validator("content")
    def content_cannot_be_empty_string(cls, value):
        if value.strip() == "":
            raise PydanticCustomError(
                "invalid content",
                "Content cannot be empty string",
            )
        return value


class TicketMessageOutSchema(BaseModel):
    id: int
    receiver: EmailStr
    sender: EmailStr
    content: str
