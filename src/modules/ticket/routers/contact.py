from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.modules.ticket.schemas import CreateContactSchema
from src.modules.ticket.services.contact import contact_service

router = APIRouter()


@router.post("/contacts", summary="Creates new contact")
async def register_contact(
    payload: CreateContactSchema, db: AsyncSession = Depends(get_db)
):
    return await contact_service.create_contact(db, payload)


@router.get("/contacts", summary="Get all contacts")
async def list_contacts(db: AsyncSession = Depends(get_db)):
    return await contact_service.list_contacts(db)
