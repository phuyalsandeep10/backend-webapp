from datetime import datetime, timedelta
from typing import Optional

from cachetools import TTLCache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.common.context import TenantContext, UserContext
from src.config.settings import settings
from src.modules.auth.models import User

# Initialize cache with 5-minute TTL and 1000-item capacity
user_cache = TTLCache(maxsize=1000, ttl=300)

security = HTTPBearer()

bearer_scheme = HTTPBearer()


async def get_user_by_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

        if token in user_cache:
            return user_cache[token]

        user_email: str = payload.get("sub")

        user = await User.find_one(where={"email": user_email})

        return user
    except Exception as e:
        print("expired", e)
        return None


async def validate_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    isEmailVerifyCheck: Optional[bool] = True,
    isTwoFaVerifyCheck: Optional[bool] = True,
):
    """Get current authenticated user"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = (
            credentials.credentials.split(" ")[-1]
            if " " in credentials.credentials
            else credentials.credentials
        )

        user = await get_user_by_token(token)

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        #@Todo: we need to enable this after adding email verification
        
        # if isEmailVerifyCheck and not user.email_verified_at:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Email not verified",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )

        # if isTwoFaVerifyCheck and user.two_fa_enabled and not user.is_2fa_verified:

        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED, detail="Two FA not "
        #     )

        user_cache[token] = user  # Cache the user object

        # setting the user_id to the user_context
        UserContext.set(user.id)

        # setting the organization_id to the tenantcontext
        organization_id = user.attributes.get("organization_id")
        if organization_id:
            TenantContext.set(organization_id)

        return user

    except JWTError as e:
        print("JWTError:", e)
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await validate_user(credentials=credentials)


def get_current_user_factory(
    isEmailVerifyCheck: bool = False, isTwoFaVerifyCheck: bool = False
):
    async def current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        return await validate_user(
            credentials=credentials,
            isEmailVerifyCheck=isEmailVerifyCheck,
            isTwoFaVerifyCheck=isTwoFaVerifyCheck or False,
        )

    return current_user


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return (
        credentials.credentials.split(" ")[-1]
        if " " in credentials.credentials
        else credentials.credentials
    )


def update_user_cache(token: str, user: User):
    user_cache[token] = user


def invalidate_user_cache(token: str):
    user_cache.pop(token, None)


def create_access_token(
    data: dict, expires_duration: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
):
    to_encode = data.copy()

    expire = datetime.utcnow() + (timedelta(minutes=expires_duration))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
