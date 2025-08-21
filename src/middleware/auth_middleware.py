import logging
from typing import List, Optional

import jwt

from src.common.context import TenantContext, UserContext
from src.config.settings import settings
from src.modules.auth.models import User
from src.utils.response import CustomResponse as cr
from jwt.exceptions import ExpiredSignatureError


logger = logging.getLogger(__name__)


from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_user_by_token, extemp_paths: Optional[List[str]]):
        super().__init__(app)
        self.get_user_by_token = (
            get_user_by_token  # async function to get user from token
        )
        self.extemp_paths = extemp_paths

    async def dispatch(self, request: Request, call_next):
        print(f"Request path: {request.url.path}")

        if request.method == "OPTIONS":
            return await call_next(request)

        # skip protected or extempted paths
        if self.extemp_paths and any(
            request.url.path.startswith(path) for path in self.extemp_paths
        ):
            print(f"Exempting path: {request.url.path}")
            return await call_next(request)

        try:
            auth_header = request.headers.get("Authorization", None)
            if not auth_header or not auth_header.startswith("Bearer"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid Authorization header",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                user_email: str = payload.get("sub", None)
                user = await User.find_one(where={"email": user_email})

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                UserContext.set(user.id)
                organization_id = user.attributes.get("organization_id")
                if organization_id:
                    TenantContext.set(organization_id)
                else:
                    TenantContext.set(None)

                response = await call_next(request)
                return response
            except ExpiredSignatureError as e:
                logging.error(e)
                return cr.error(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="Authentication failed",
                    data=str(e),
                )

        except Exception as e:
            logging.error(e)
            return cr.error(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Authentication required",
                data=str(e),
            )
