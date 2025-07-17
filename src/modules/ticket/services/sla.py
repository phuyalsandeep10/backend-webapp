from fastapi import HTTPException, status

from src.common.dependencies import get_user_by_token
from src.modules.ticket.models import SLA
from src.modules.ticket.schemas import CreateSLASchema
from src.utils.response import CustomResponse as cr


class SLAServices:

    async def register_sla(self, payload: CreateSLASchema, authorization: str):
        try:
            # finding the user id from the request access token
            token = authorization.split(" ")[1]
            if authorization.split(" ")[0] != "Bearer":
                raise IndexError()
            user = await get_user_by_token(token)

            if not user:
                raise HTTPException(status_code=403, detail="Authorization denied")

            user_id = user.id
            data = dict(payload)
            data["issued_by"] = user_id

            sla = await SLA.create(**data)

            if not sla:
                return cr.error(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Error while registering Service Level Agreement",
                )

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully registered the Service Level Agreement",
                data=sla.to_dict(),
            )
        except IndexError as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Token required in standard format",
            )

        except HTTPException:

            raise

        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while registering Service Level Agreement",
            )

    async def list_slas(self):
        try:
            sla_list = await SLA.get_all()
            slas = [s.to_dict() for s in sla_list]

            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully fetched all the sla",
                data=slas,
            )

        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while fetching Service Level Agreement",
            )


sla_service = SLAServices()
