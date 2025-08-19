from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING, Optional
from src.common.models import CommonModel


if TYPE_CHECKING:
    from src.modules.staff_managemet.models.permissions import Permissions
    from src.modules.organizations.models import OrganizationRole


class RolePermission(CommonModel, table=True):
    __tablename__ = "role_permissions"

    permission_id: int = Field(
        foreign_key="permissions.id",
        index=True,
        nullable=False,
    )

    role_id: int = Field(
        foreign_key="org_roles.id",
        index=True,
        nullable=False,
    )

    is_changeable: bool = Field(default=False)
    is_deletable: bool = Field(default=False)
    is_viewable: bool = Field(default=False)

    permission: Optional["Permissions"] = Relationship(
        back_populates="role_permissions"
    )
    org_role: "OrganizationRole" = Relationship(back_populates="role_permissions")
