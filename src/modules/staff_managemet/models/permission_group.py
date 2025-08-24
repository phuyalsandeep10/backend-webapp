from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from src.common.models import BaseModel


if TYPE_CHECKING:
    from src.modules.staff_managemet.models.permissions import Permissions


class PermissionGroup(BaseModel, table=True):
    __tablename__ = "sys_permissions_groups"

    name: str = Field(max_length=255, index=True)

    permissions: List["Permissions"] = Relationship(back_populates="group")
