from src.models import User, OrganizationMember
from fastapi import Depends, HTTPException, status

from src.common.dependencies import get_current_user

from typing import List


async def is_organization_owner(
    organization_id: int,
    user: User = Depends(get_current_user),
):
    member = OrganizationMember.find_one(
        where={"organization_id": organization_id, "user_id": user.id, "is_owner": True}
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this organization.",
        )
    return True


def is_superuser(user: User = Depends(get_current_user)):
    if not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Forbidden: Superuser role required"
        )
    return user


def has_permissions(required_perms: List[str]):
    def dependency(current_user=Depends(get_current_user)):
        # Assume current_user.permissions is List[str]
        missing = [p for p in required_perms if p not in current_user.permissions]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {missing}",
            )
        return current_user

    return dependency
