from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException
from src.models import PermissionGroup, Permissions, RolePermission, OrganizationRole
from src.modules.staff_managemet.schemas.permission_group import (
    PermissionOutSchema,
)
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


@router.post("/permission-groups", response_model=Dict[str, Any])
async def get_permission_groups_with_role_perms(
    role_id: int,
    current_user=Depends(get_current_user),
):
    groups = await PermissionGroup.filter()
    all_permissions = await Permissions.filter()
    role_perms = await RolePermission.filter(where={"role_id": role_id})

    role_perm_map = {rp.permission_id: rp for rp in role_perms}

    perms_by_group_id = {}
    for perm in all_permissions:
        perms_by_group_id.setdefault(perm.group_id, []).append(perm)

    response = {}
    for group in groups:
        perms = perms_by_group_id.get(group.id, [])
        perms_list = []
        for perm in perms:
            schema_data = PermissionOutSchema.model_validate(perm).model_dump()

            rp = role_perm_map.get(perm.id)
            if rp is not None:
                schema_data.update(
                    {
                        "is_changeable": rp.is_changeable,
                        "is_deletable": rp.is_deletable,
                        "is_viewable": rp.is_viewable,
                    }
                )

            perms_list.append(PermissionOutSchema(**schema_data))

        response[group.name] = perms_list

    response["role_permissions"] = [
        {
            "permission_id": rp.permission_id,
            "is_changeable": rp.is_changeable,
            "is_deletable": rp.is_deletable,
            "is_viewable": rp.is_viewable,
        }
        for rp in role_perms
    ]

    return response
