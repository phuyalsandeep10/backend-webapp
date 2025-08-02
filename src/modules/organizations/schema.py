from pydantic import BaseModel, Field, EmailStr
from typing import List


class OrganizationSchema(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the organization")
    description: str | None = Field(
        None, max_length=500, description="Description of the organization"
    )
    domain:str = Field(..., max_length=255, description="Domain of the organization")
    # slug: str = Field(..., max_length=255, description="Unique slug for the organization")
    logo: str | None = Field(
        None, max_length=255, description="Logo URL for the organization"
    )
    purpose: str | None = Field(
        None, max_length=255, description="Purpose of organization creation"
    )


class OrganizationRoleSchema(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the role")
    description: str | None = Field(
        None, max_length=500, description="Description of the role"
    )
    permissions: list[str] = Field([])


class PermissionSchema(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=250)


class OrganizationInviteSchema(BaseModel):
    email: EmailStr
    role_ids: List[int]


class OrganizationInvitationApproveSchema(BaseModel):
    email: EmailStr
    token: str


class AssignRoleSchema(BaseModel):
    user_id: int
    role_id: int


class AssignPermissionSchema(BaseModel):
    permission_ids: List[int]
