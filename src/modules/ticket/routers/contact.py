from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.modules.ticket.schemas import CreateContactSchema
from src.modules.ticket.services.contact import contact_service

router = APIRouter()


@router.post("/contacts", summary="Creates new contact")
async def register_contact(payload: CreateContactSchema):
    return await contact_service.create_contact(payload)


@router.get("/contacts", summary="Get all contacts")
async def list_contacts():
    return await contact_service.list_contacts()


@router.delete("/contacts/{contact_id}", summary="Delete a contact")
async def delete_contact(contact_id: int):
    return await contact_service.delete_contact(contact_id)
