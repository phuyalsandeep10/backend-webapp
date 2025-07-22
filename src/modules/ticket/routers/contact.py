from typing import List

from fastapi import APIRouter

from src.modules.ticket.schemas import ContactOut, CreateContactSchema
from src.modules.ticket.services.contact import contact_service
from src.utils.response import CustomResponseSchema

router = APIRouter()


@router.post(
    "/contacts", summary="Creates new contact", response_model=CustomResponseSchema
)
async def register_contact(payload: CreateContactSchema):
    return await contact_service.create_contact(payload)


@router.get(
    "/contacts",
    summary="Get all contacts",
    response_model=CustomResponseSchema[List[ContactOut]],
)
async def list_contacts():
    print("Triggered")
    return await contact_service.list_contacts()


@router.get(
    "/contacts/{contact_id}",
    summary="Get a contact",
    response_model=CustomResponseSchema[ContactOut],
)
async def get_contact(contact_id: int):
    return await contact_service.get_contact(contact_id)


@router.delete(
    "/contacts/{contact_id}",
    summary="Delete a contact",
    response_model=CustomResponseSchema,
)
async def delete_contact(contact_id: int):
    return await contact_service.delete_contact(contact_id)
