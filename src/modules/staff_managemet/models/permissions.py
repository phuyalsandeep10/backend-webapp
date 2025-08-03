# src/modules/staff_management/models/permission.py
from typing import Optional
from sqlmodel import Field, Relationship
from src.common.models import BaseModel
from src.modules.staff_managemet.models.permission_group import PermissionGroup


class Permission(BaseModel, table=True):
    __tablename__ = "sys_permissions"

    name: str = Field(max_length=255, index=True, unique=True)

    group_id: int = Field(foreign_key="sys_permission_groups.id")
    group: Optional[PermissionGroup] = Relationship(back_populates="permissions")
