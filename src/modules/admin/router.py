from src.common.models import Permission
from .dto import PermissionDto
from fastapi import APIRouter, Depends, HTTPException
from src.common.permissions import is_superuser


router = APIRouter(prefix="/permissions")


@router.get("")
def get_permissions(user=Depends(is_superuser)):
    return Permission.filter()


@router.post("")
def create_permissions(body: PermissionDto, user=Depends(is_superuser)):
    record = Permission.find_one(
        {
            "name": {"mode": "insensitive", "value": body.name},
        }
    )

    if record:
        raise HTTPException(400, "Duplicate Name")

    record = Permission.find_one(
        {"identifier": {"mode": "insensitive", "value": body.identifier}}
    )

    if record:
        raise HTTPException(400, "Duplicate Identifier")

    return Permission.create(
        name=body.name, identifier=body.identifier, description=body.description
    )


@router.put("/{permission_id}")
def update_permission(
    permission_id: int, body: PermissionDto, user=Depends(is_superuser)
):
    existing_record = Permission.get(permission_id)

    if not existing_record:
        raise HTTPException(404, "Don't found")

    record = Permission.find_one(
        {
            "name": {"mode": "insensitive", "value": body.name},
        }
    )

    if record and record.id != existing_record.id:
        raise HTTPException(400, "Duplicate Name")

    record = Permission.find_one(
        {"identifier": {"mode": "insensitive", "value": body.identifier}}
    )

    if record and record.id != existing_record.id:
        raise HTTPException(400, "Duplicate Identifier")

    return Permission.update(
        permission_id,
        name=body.name,
        description=body.description,
        identifier=body.identifier,
    )
