from pydantic import BaseModel, Field, EmailStr
from typing import List


class OrganizationDto(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the organization")
    description: str | None = Field(
        None, max_length=500, description="Description of the organization"
    )
    # slug: str = Field(..., max_length=255, description="Unique slug for the organization")
    logo: str | None = Field(
        None, max_length=255, description="Logo URL for the organization"
    )
    purpose: str | None = Field(
        None, max_length=255, description="Purpose of organization creation"
    )
    website: str | None = Field(
        None, max_length=255, description="Website URL for the organization"
    )


class OrganizationRoleDto(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the role")
    description: str | None = Field(
        None, max_length=500, description="Description of the role"
    )
    permissions: list[str] = Field([])


class PermissionDto(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=250)


class OrganizationInviteDto(BaseModel):
    email: EmailStr
    role_ids: List[int]


class OrganizationInvitationApproveDto(BaseModel):
    email: EmailStr
    token: str


class AssignRoleDto(BaseModel):
    user_id: int
    role_id: int


class AssignPermissionDto(BaseModel):
    permission_ids: List[int]
