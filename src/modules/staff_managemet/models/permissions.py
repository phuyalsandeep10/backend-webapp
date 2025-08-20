from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Column, Field, Relationship, ForeignKey
from src.common.models import BaseModel
from src.modules.staff_managemet.models.role_permission import RolePermission


if TYPE_CHECKING:
    from src.modules.staff_managemet.models.permission_group import PermissionGroup


class Permissions(BaseModel, table=True):
    __tablename__ = "permissions"

    name: str = Field(max_length=255, index=True, unique=True)

    group_id: int = Field(
        sa_column=Column(
            ForeignKey("sys_permissions_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )

    group: Optional["PermissionGroup"] = Relationship(back_populates="permissions")

    role_permissions: List["RolePermission"] = Relationship(back_populates="permission")
