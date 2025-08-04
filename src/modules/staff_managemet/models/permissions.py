from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from src.common.models import BaseModel


if TYPE_CHECKING:
    from src.modules.staff_managemet.models.permission_group import PermissionGroup


class Permissions(BaseModel, table=True):
    __tablename__ = "permissions"

    name: str = Field(max_length=255, index=True, unique=True)

    group_id: Optional[int] = Field(
        default=None, foreign_key="sys_permissions_groups.id"
    )
    group: Optional["PermissionGroup"] = Relationship(back_populates="permissions")
