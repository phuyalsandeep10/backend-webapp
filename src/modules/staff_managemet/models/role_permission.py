from sqlmodel import Field
from typing import TYPE_CHECKING
from src.common.models import CommonModel


if TYPE_CHECKING:
    from src.modules.staff_managemet.models.permissions import Permission
    from src.modules.organizations.models import OrganizationRole


class RolePermission(CommonModel, table=True):
    __tablename__ = "sys_role_permissions"

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

    role_id: int = Field()

    is_changeable: bool = Field(default=False)
    is_deletable: bool = Field(default=False)
    is_viewable: bool = Field(default=False)
