from typing import List, Optional
from sqlmodel import Field, Relationship
from src.common.models import BaseModel
from src.modules.staff_managemet.models.permissions import Permission


class PermissionGroup(BaseModel, table=True):
    __tablename__ = "sys_permission_groups"

    name: str = Field(max_length=255, index=True)

    permissions: List[Permission] = Relationship(back_populates="group")
