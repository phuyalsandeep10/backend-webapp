from typing import Dict, List
from fastapi import APIRouter, Depends
from src.models import PermissionGroup, Permissions
from src.modules.staff_managemet.schemas.permission_group import PermissionOutSchema
from src.common.dependencies import get_current_user

router = APIRouter()


@router.get("/permission-groups", response_model=Dict[str, List[PermissionOutSchema]])
async def get_permission_groups(current_user=Depends(get_current_user)):
    groups = await PermissionGroup.filter()
    all_permissions = await Permissions.filter()

    perms_by_group_id = {}
    for perm in all_permissions:
        perms_by_group_id.setdefault(perm.group_id, []).append(perm)

    response = {}
    for group in groups:
        perms = perms_by_group_id.get(group.id, [])
        perms_list = [PermissionOutSchema.model_validate(perm) for perm in perms]
        response[group.name] = perms_list

    return response
