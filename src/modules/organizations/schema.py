from pydantic import BaseModel, Field, EmailStr
from typing import List
from typing import Optional


class OrganizationSchema(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the organization")
    description: str | None = Field(
        None, max_length=500, description="Description of the organization"
    )
    domain: str = Field(..., max_length=255, description="Domain of the organization")

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
    # permissions: List[UpdateRoleInSchema] = []

    # permissions: list[str] = Field([])


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


class RolePermissionInSchema(BaseModel):
    role_id: int
    permission_id: int
    value: bool = False


class CreateRoleOutSchema(BaseModel):
    role_id: int
    role_name: str
    description: str
    org_name: str


class UpdateRoleInSchema(BaseModel):
    permission_id: int
    is_changeable: bool = False
    is_deletable: bool = False
    is_viewable: bool = False


class UpdateRoleInfoSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the role")
    description: str | None = Field(
        None, max_length=500, description="Description of the role"
    )
    permissions: List[UpdateRoleInSchema] = []


class CreateRoleSchema(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    permissions: List[UpdateRoleInSchema] = []


class CreateRoleOutSchema(BaseModel):
    role_id: int
    role_name: str
    description: str
    org_name: str
    created_at: str
    no_of_agents: int
    permission_summary: List[UpdateRoleInSchema] = []