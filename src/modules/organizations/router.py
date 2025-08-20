import logging
from fastapi import APIRouter, Depends, HTTPException, logger, status
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from src.modules.organizations.models import OrganizationRole, OrganizationMemberRole
from typing import List, Optional
from fastapi.logger import logger
import base64
import secrets



from src.common.dependencies import (
    get_bearer_token,
    get_current_user,
    update_user_cache,
    validate_role_data,
)
from src.common.models import Permission
from src.common.utils import random_unique_key
from src.config.settings import settings
from src.enums import InvitationStatus
from src.models import (
    Organization,
    OrganizationInvitation,
    OrganizationMember,
    OrganizationMemberRole,
    OrganizationRole,
    User,
    OrganizationInvitationRole,
)
from src.models.countries import Country
from src.models.timezones import Timezone
from src.tasks import send_invitation_email
from src.utils.response import CustomResponse as cr
from src.modules.staff_managemet.models import RolePermission
from .schema import (
    OrganizationSchema,
    OrganizationInviteSchema,
    AssignRoleSchema,
    CreateRoleOutSchema,
    UpdateRoleInfoSchema,
    CreateRoleSchema,
    InvitationOut,
)

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("")
async def get_organizations(user=Depends(get_current_user)):
    """
    Get the list of organizations the user belongs to.
    """
    print("The user is", user.id)
    records = await Organization.get_orgs_by_user_id(user_id=user.id)
    data = [item.to_json() for item in records]
    return cr.success(data=data)


@router.post("")
async def create_organization(
    body: OrganizationSchema,
    user=Depends(get_current_user),
    token: str = Depends(get_bearer_token),
):
    """
    Create a new organization.
    """
    errors = []
    record = await Organization.find_one(
        where={"name": {"mode": "insensitive", "value": body.name}, "owner_id": user.id}
    )

    if record:
        errors.append({"name": "this organization with this name already exists"})

    record = await Organization.find_one(
        where={
            "domain": {"mode": "insensitive", "value": body.domain},
        }
    )

    if record:
        errors.append({"domain": "This domain already exists"})

    if errors:
        return cr.error(data=errors)

    email_alias = ""
    while True:
        # generating the random email
        token_bytes = secrets.token_bytes(9)

        # Encode to Base64 URL-safe string
        email_alias_name = (
            base64.urlsafe_b64encode(token_bytes).rstrip(b"=").decode("ascii")
        )

        email_alias = f"{email_alias_name}@{settings.EMAIL_DOMAIN}"

        # checking it the email alias exists before
        record = await Organization.find_one(
            where={"email_alias": {"mode": "insensitive", "value": email_alias}}
        )
        if record:
            continue
        break

    slug = body.name.lower().replace(" ", "-")

    organization = await Organization.create(
        name=body.name,
        description=body.description,
        slug=slug,
        logo=body.logo,
        domain=body.domain,
        purpose=body.purpose,
        identifier=f"{slug}-{random_unique_key()}",
        owner_id=user.id,
        email_alias=email_alias,
    )

    await OrganizationMember.create(
        organization_id=organization.id, user_id=user.id, is_owner=True
    )

    user_attributes = user.attributes

    if not user_attributes:
        user_attributes = {}

    if "organization_id" not in user_attributes:
        user = await User.update(
            user.id, attributes={"organization_id": organization.id}
        )

        if not user:
            raise HTTPException(404, "Not found User")

        update_user_cache(token, user)

    return cr.success(data=organization.to_json())


@router.get("/{organization_id}/members")
async def get_members(user=Depends(get_current_user)):
    organization_id = user.attributes.get("organization_id")
    members = await OrganizationMember.filter(
        {
            "organization_id": organization_id,
        }
    )

    # For each member, fetch their roles
    result = []
    for member in members:
        # Get all member_role entries for this member
        member_roles = await OrganizationMemberRole.filter({"member_id": member.id})
        # Get role names
        roles = []
        for mr in member_roles:
            role = await OrganizationRole.get(mr.role_id)
            if role:
                roles.append({"id": role.id, "name": role.name})
        # Add roles to member dict
        member_dict = member.dict() if hasattr(member, "dict") else dict(member)
        member_dict["roles"] = roles
        result.append(member_dict)
    return cr.success(data=result)


@router.put("/{organization_id}")
async def update_organization(
    organization_id: int, body: OrganizationSchema, user=Depends(get_current_user)
):
    """
    Update an existing organization.
    """

    organization = await Organization.get(organization_id)

    organization_member = await OrganizationMember.find_one(
        {"organization_id": organization_id, "user_id": user.id}
    )

    if not organization_member:
        return cr.error(
            data={"success": False},
            message="You do not have permission to update this organization",
        )

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if organization.name != body.name:
        existing_org = await Organization.find_one(
            {"name": {"value": body.name, "mode": "insensitive"}}
        )
        if existing_org:
            return cr.error(
                data={"success": False},
                message="Organization with this name already exists",
            )
    record = await Organization.find_one(
        where={
            "domain": {"mode": "insensitive", "value": body.domain},
        }
    )

    if record and record.domain != body.domain:
        return cr.error(
            data={"success": False}, message="This domain is already exists"
        )

    record = await Organization.update(
        organization_id,
        name=body.name,
        description=body.description,
        logo=body.logo,
        domain=body.domain,
    )

    return cr.success(data=record)


@router.put("/{organization_id}/set")
async def set_organization(
    organization_id: int,
    user=Depends(get_current_user),
    token: str = Depends(get_bearer_token),
):
    """
    Set an existing organization.
    """

    organization = await Organization.get(organization_id)

    user = await User.update(user.id, attributes={"organization_id": organization_id})

    if not user:
        raise HTTPException(404, "Not found User")

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    update_user_cache(token, user)

    return cr.success(data={"message": "Organization set successfully"})


@router.post("/roles")
async def create_role(body: CreateRoleSchema, user=Depends(get_current_user)):
    """
    Create a New Role for an organization.
    """
    try:
        await validate_role_data(
            name=body.name,
            permissions=body.permissions,
            permission_group_id=body.permission_group,
        )

        # Create on Organzation Role
        role = await OrganizationRole.create(
            **body.model_dump(
                exclude={"permissions", "updated_at", "created_at"}, exclude_none=True
            ),
            identifier=body.name.lower().replace(" ", "-"),
        )

        # Create on role Permission Table
        role_permission_ids = []
        for perm in body.permissions:
            role_perm = await RolePermission.create(
                role_id=role.id,
                **perm.model_dump(),
            )
            role_permission_ids.append(role_perm.id)

        # update the attributes Column of Org_role
        await OrganizationRole.update(
            id=role.id,
            attributes={"no_of_agents": 0, "permissions": role_permission_ids},
        )

        return cr.success(data=None, message="Role created successfully")

    except Exception as e:
        logger.exception(e)
        return cr.error(
            status_code=getattr(
                e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            message=f"{e.detail if hasattr(e, 'detail') else str(e)}",
            data=str(e),
        )


# @router.put("/roles/{role_id}")
# async def update_role(
#     role_id: int, body: UpdateRoleInfoSchema, user=Depends(get_current_user)
# ):
#     """
#     Update an existing role within the current tenant's organization.
#     """

#     role = await OrganizationRole.find_one(where={"id": role_id})

#     if not role:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
#         )

#     if not body.name or body.name.strip() == "":
#         raise HTTPException(
#             status_code=status.HTTP_406_NOT_ACCEPTABLE,
#             detail="Role name cannot be empty",
#         )

#     if not any(
#         perm.is_changeable or perm.is_deletable or perm.is_viewable
#         for perm in body.permissions
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_406_NOT_ACCEPTABLE,
#             detail="Minimum of one permission is required",
#         )

#     existing = await OrganizationRole.find_one(
#         where={"name": {"value": body.name, "mode": "insensitive"}}
#     )

#     if existing and existing.id != role.id:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT, detail="Role name already exists"
#         )

#     permission_group_id = body.permission_group

#     for perm in body.permissions:
#         permission = await Permissions.find_one(where={"id": perm.permission_id})
#         if not permission:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No such permission with id {perm.permission_id}",
#             )
#         if permission.group_id != permission_group_id:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Permission {perm.permission_id} does not belong to group {permission_group_id}",
#             )

#     await OrganizationRole.update(
#         role_id,
#         **body.model_dump(exclude={"permissions", "permission_group"}),
#         identifier=body.name.lower().replace(" ", "-"),
#     )

#     for perm in body.permissions:
#         role_perm = await RolePermission.find_one(
#             where={"role_id": role.id, "permission_id": perm.permission_id}
#         )
#         if role_perm:
#             await RolePermission.update(
#                 role_perm.id,
#                 **perm.model_dump(),
#             )

#     # updated_role = await OrganizationRole.find_one(where={"id": role_id})
#     return cr.success(data=None, messasge="Role Updated Successfully")


# ----------------------------------


@router.put("/roles/{role_id}")
async def updte_role(
    role_id: int, body: UpdateRoleInfoSchema, user=Depends(get_current_user)
):
    try:
        role = await OrganizationRole.find_one(where={"id": role_id})
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        await validate_role_data(
            name=body.name,
            permissions=body.permissions,
            role_id=role_id,
            permission_group_id=body.permission_group,
        )

        await OrganizationRole.update(
            role_id,
            **body.model_dump(exclude={"permissions", "permission_group"}),
            identifier=body.name.lower().replace(" ", "-"),
        )

        role_permission_ids = []

        for perm in body.permissions:
            role_perm = await RolePermission.find_one(
                where={"role_id": role.id, "permission_id": perm.permission_id}
            )

            if role_perm:
                data = perm.model_dump(exclude={"permission_id"})
                await RolePermission.update(role_perm.id, **data)
                role_permission_ids.append(role_perm.id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission {perm.permission_id} does not exist for this role.",
                )

        no_of_agents = (role.attributes or {}).get("no_of_agents")
        await OrganizationRole.update(
            id=role.id,
            attributes={
                "no_of_agents": no_of_agents,
                "permissions": role_permission_ids,
            },
        )

        return cr.success(data=None, message="Role Updated Successfully")

    except Exception as e:
        logger.exception(e)
        return cr.error(
            status_code=getattr(
                e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            message=f"{e.detail if hasattr(e, 'detail') else str(e)}",
            data=str(e),
        )


@router.get("/roles")
async def get_roles(user=Depends(get_current_user)):
    """
    List all roles with no. of agents and permission summary from attributes JSON
    """
    try:
        roles = await OrganizationRole.filter(
            related_items=[
                selectinload(OrganizationRole.role_permissions).selectinload(
                    RolePermission.permission
                ),
                # selectinload(OrganizationRole.attributes)
            ]
        )

        results = []
        for role in roles:
            no_of_agents = role.attributes.get("no_of_agents", 0)

            role_data = role.to_json(CreateRoleOutSchema)
            role_data["role_id"] = role.id
            role_data["role_name"] = role.name
            role_data["no_of_agents"] = no_of_agents

            permission_summary = []
            permission_ids = role.attributes.get("permissions", [])

            for rp in role.role_permissions:
                if rp.id in permission_ids:
                    permission_summary.append(
                        {
                            "permission_name": (
                                rp.permission.name if rp.permission else None
                            ),
                            "is_changeable": rp.is_changeable,
                            "is_deletable": rp.is_deletable,
                            "is_viewable": rp.is_viewable,
                        }
                    )

            role_data["permission_summary"] = permission_summary
            results.append(role_data)

        return cr.success(data=results, message="get roles successful")
    except Exception as e:
        logger.exception(e)
        return cr.error(
            status_code=getattr(
                e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            message=f"{e.detail if hasattr(e, 'detail') else str(e)}",
            data=str(e),
        )


@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, user=Depends(get_current_user)):
    """
    Soft delete a role from the organization (tenant-aware).
    """
    try:
        await OrganizationRole.soft_delete(where={"id": role_id})

        return cr.success(data={"message": "Role deletion successful"})
    except Exception as e:
        logger.exception(e)
        return cr.error(
            status_code=getattr(
                e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            message=f"{e.detail if hasattr(e, 'detail') else str(e)}",
            data=str(e),
        )


@router.post("/invitation")
async def invite_user(body: OrganizationInviteSchema, user=Depends(get_current_user)):
    record = await OrganizationInvitation.find_one(
        where={"email": body.email, "status": "pending"}
    )

    if record:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An invitation already exists for this email.",
        )

    if user.email == body.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can't invite yourself."
        )

    expires_at = datetime.utcnow() + timedelta(days=7)

    invitations = await OrganizationInvitation.create(
        **body.model_dump(),
        invited_by_id=user.id,
        status="pending",
        token="",
        expires_at=expires_at,
    )

    for role_id in body.role_ids:
        await OrganizationInvitationRole.create(
            invitation_id=invitations.id, role_id=role_id
        )

    send_invitation_email.delay(email=body.email)

    return cr.success(data=None, message="Invitation sent successfully")


@router.get("/invitation", response_model=List[InvitationOut])
async def get_invitations(user=Depends(get_current_user)):
    invitations = await OrganizationInvitation.filter()

    data = [inv.to_json(schema=InvitationOut) for inv in invitations]
    return cr.success(data=data)


@router.post("/invitation/{invitation_id}/reject")
async def reject_invitation(invitation_id: int, user=Depends(get_current_user)):
    invitation = await OrganizationInvitation.get(invitation_id)

    if not invitation:
        raise HTTPException(404, "Not found")

    record = await OrganizationInvitation.update(
        invitation.id, status=InvitationStatus.REJECTED
    )
    return cr.success(data=record)


@router.post("/invitation/{invitation_id}/accept")
async def accept_invitation(invitation_id: int, user=Depends(get_current_user)):
    invitation = await OrganizationInvitation.find_one(where={"id": invitation_id})

    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if user.email != invitation.email:
        raise HTTPException(
            status_code=403, detail="Unauthorized to accept this invitation"
        )

    await OrganizationInvitation.update(invitation.id, status=InvitationStatus.ACCEPTED)

    member = await OrganizationMember.find_one(
        where={"organization_id": invitation.organization_id, "user_id": user.id}
    )
    if not member:
        member = await OrganizationMember.create(
            organization_id=invitation.organization_id, user_id=user.id
        )

    if invitation.role_ids:
        for role_id in invitation.role_ids:
            # Make sure RolePermission entry does not duplicate if it already exists
            existing = await OrganizationMemberRole.find_one(
                where={"role_id": role_id, "member_id": member.id}
            )
            if not existing:
                await OrganizationMemberRole.create(
                    role_id=role_id, member_id=member.id
                )

    await User.update(user.id, name=invitation.name)

    return cr.success(data={"message": "Invitation successfully accepted"})


@router.delete("/invitations/{invitation_id}")
async def delete_invitation(invitation_id: int, user=Depends(get_current_user)):
    """
    Soft delete an invitation from the organization (tenant-aware).
    """
    await OrganizationInvitation.soft_delete(where={"id": invitation_id})

    return cr.success(data={"message": "Invitation successfully deleted"})


@router.post("/roles-assign")
async def assign_role(body: AssignRoleSchema, user=Depends(get_current_user)):
    organization_id = user.attributes.get("organization_id")
    member = await OrganizationMember.find_one(
        where={"organization_id": organization_id, "user_id": body.user_id}
    )

    if not member:
        raise HTTPException(400, "Organization Member not found")

    member_role = await OrganizationMemberRole.find_one(
        where={"member_id": member.id, "role_id": body.role_id}
    )

    if not member_role:
        await OrganizationMemberRole.create(role_id=body.role_id, member_id=member.id)

    return cr.success(data={"message": "Successfully assign"})


@router.post("/remove-assign-role")
async def remove_assign_role(body: AssignRoleSchema, user=Depends(get_current_user)):
    organization_id = user.attributes.get("organization_id")

    member = await OrganizationMember.find_one(
        where={"organization_id": organization_id, "user_id": body.user_id}
    )

    if not member:
        raise HTTPException(400, "Organization Member not found")

    member_role = await OrganizationMemberRole.find_one(
        {"member_id": member.id, "role_id": body.role_id}
    )

    if not member_role:
        raise HTTPException(400, "Role not found")

    await OrganizationMemberRole.soft_delete(member_role.id)
    return cr.success(data={"message": "Successfully remove role"})


@router.get("/permissions")
async def get_permissions(user=Depends(get_current_user)):
    permissions = await Permission.filter()
    return cr.success(data=permissions)


@router.get("/countries")
async def get_countries():
    """Get all countries for selection"""
    try:
        countries = await Country.filter()

        countries_data = [
            {
                "id": country.id,
                "name": country.name,
                "code": country.iso_code_2,
                "iso_code_2": country.iso_code_2,  # US
                "iso_code_3": country.iso_code_3,  # USA
                "phone_code": country.phone_code,  # +977
            }
            for country in countries
        ]

        return cr.success(
            data={"countries": countries_data},
            message="Countries retrieved successfully",
        )
    except Exception as e:
        return cr.error(message=f"Failed to retrieve countries: {str(e)}")


@router.get("/timezones")
async def get_timezones(country_id: Optional[int] = None):
    """Get all timezones, optionally filtered by country_id"""
    try:
        where_clause = {}
        if country_id:
            where_clause["country_id"] = country_id

        timezones = await Timezone.filter(
            where=where_clause,
            related_items=[
                selectinload(Timezone.country)
            ],  # for loading countries relationship
        )

        timezones_data = [
            {
                "id": tz.id,
                "name": tz.name,
                "display_name": tz.display_name,
                "country_id": tz.country_id,
                "country_name": tz.country.name if tz.country else None,
            }
            for tz in timezones
        ]

        return cr.success(
            data={"timezones": timezones_data},
            message="Timezones retrieved successfully",
        )

    except Exception as e:
        return cr.error(message=f"Failed to retrieve timezones: {str(e)}")
