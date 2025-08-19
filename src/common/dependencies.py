from datetime import datetime, timedelta
from typing import Optional

from cachetools import TTLCache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.common.context import TenantContext, UserContext
from src.config.settings import settings
from src.modules.auth.models import User
from src.modules.organizations.models import OrganizationRole
from src.modules.staff_managemet.models import Permissions

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

    print("couldn't validate user")
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


async def _validate_role_name(name: str, role_id: int = None):
    """
    Check name is not empty and unique (ignoring current role if updating).
    """
    if not name or name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Role name cannot be empty",
        )

    existing_role = await OrganizationRole.find_one(
        where={"name": {"mode": "insensitive", "value": name}}
    )
    if existing_role and (role_id is None or existing_role.id != role_id):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT if role_id else status.HTTP_406_NOT_ACCEPTABLE
            ),
            detail="Role name already exists",
        )


async def _validate_permissions_exist(permissions: list):
    """
    Ensure all permissions exist in the database.
    """
    for perm in permissions:
        permission = await Permissions.find_one(where={"id": perm.permission_id})
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No such permission with id {perm.permission_id}",
            )


async def _validate_permission_group(permissions: list, group_id: int):
    """
    Check that all permissions belong to the correct permission group.
    """
    for perm in permissions:
        permission = await Permissions.find_one(where={"id": perm.permission_id})
        if permission.group_id != group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission {perm.permission_id} does not belong to group {group_id}",
            )


def _validate_minimum_permission(permissions: list):
    """
    At least one permission action must be True.
    """
    if not any(
        perm.is_changeable or perm.is_deletable or perm.is_viewable
        for perm in permissions
    ):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Minimum of one permission is required",
        )


async def validate_role_data(
    name: str, permissions: list, permission_group_id: int, role_id: int = None
):
    """
    Call individual functions and
    Returns a list of validated permission IDs.
    """
    await _validate_role_name(name, role_id)
    _validate_minimum_permission(permissions)
    await _validate_permissions_exist(permissions)
    await _validate_permission_group(permissions, permission_group_id)

    return [perm.permission_id for perm in permissions]
