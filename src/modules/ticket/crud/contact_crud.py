from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.modules.ticket.models import Contact
from src.modules.ticket.schemas import CreateContactSchema


async def create(db: AsyncSession, data: CreateContactSchema) -> Contact | None:

    try:
        contact = Contact(**dict(data))
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except SQLAlchemyError as e:
        print(e)
        return None


async def get_by_email(db: AsyncSession, email: str) -> Contact | None:

    try:
        result = await db.execute(select(Contact).where(Contact.email == email))
        contact = result.scalars().first()
        return contact
    except SQLAlchemyError as e:
        print(e)
        return None


async def get_all(db: AsyncSession) -> List[Contact] | None:
    try:
        result = await db.execute(select(Contact))
        contacts = result.scalars().all()
        return list(contacts)
    except SQLAlchemyError as e:
        print(e)
        return None
