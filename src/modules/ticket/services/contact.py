from typing import List

from fastapi import status
from fastapi.openapi.models import Contact
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ticket.crud import contact_crud as cc
from src.modules.ticket.schemas import CreateContactSchema
from src.utils.response import CustomResponse as cr


class ContactServices:

    async def create_contact(self, db: AsyncSession, data: CreateContactSchema):
        try:
            # checking if contact preexists or not
            pre_contact = await cc.get_by_email(db, data.email)
            if pre_contact:
                return cr.error(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Contact already exists",
                )

            contact = await cc.create(db, data)
            if contact is None:
                return cr.error(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Error while creating a contact",
                )

            return cr.success(
                status_code=status.HTTP_201_CREATED,
                message="Successfully created a contact",
                data=dict(contact),
            )
        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while creating a contact",
            )

    async def list_contacts(self, db: AsyncSession):
        try:
            contacts: List[Contact] = await cc.get_all(db)
            if not contacts:
                return cr.error(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Error while listing contacts",
                )
            contacts_data = [contact.dict() for contact in contacts]

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully fetched all contacts",
                data=contacts_data,
            )

        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while fetching all contacts",
            )


contact_service = ContactServices()
