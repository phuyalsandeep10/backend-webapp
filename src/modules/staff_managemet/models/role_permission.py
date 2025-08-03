# src/modules/staff_management/models/role_permission.py
from sqlmodel import Field
from typing import Optional
from src.common.models import BaseModel


class RolePermission(BaseModel, table=True):
    __tablename__ = "sys_role_permissions"

    permission_category_id: int = Field(foreign_key="sys_permission_groups.id")
    permission_id: int = Field(foreign_key="sys_permissions.id") 
    is_changeable: bool = Field(default=True, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    is_viewable: bool = Field(default=True, nullable=False)