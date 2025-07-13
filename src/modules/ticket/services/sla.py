from fastapi import Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ticket.crud import sla_crud as sc
from src.modules.ticket.schemas import CreateSLASchema
from src.utils.response import CustomResponse as cr


class SLAServices:

    async def register_sla(
        self, db: AsyncSession, payload: CreateSLASchema, request: Request
    ):
        try:
            # finding the user id from the request access token
            user_id = 1  # dummy id
            data = dict(payload)
            data["issued_by"] = user_id

            sla = await sc.create(db, data)

            if not sla:
                return cr.error(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Error while registering Service Level Agreement",
                )

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully registered the Service Level Agreement",
                data=dict(sla),
            )

        except Exception as e:
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while registering Service Level Agreement",
            )
