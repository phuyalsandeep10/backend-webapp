from pydantic import BaseModel
from typing import List, Optional

class PermissionOutSchema(BaseModel):
    id: int
    name: str
    group_id: int

    model_config = {"from_attributes": True}

class PermissionGroupOutSchema(BaseModel):
    id: int
    name: str
    permissions: List[PermissionOutSchema] = []
