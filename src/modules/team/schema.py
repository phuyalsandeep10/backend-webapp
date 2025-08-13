from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from src.common.models import TenantModel


class TeamSchema(BaseModel):
    name: str = Field(..., max_length=250)
    description: str | None = Field(None, max_length=300)


class TeamMemberSchema(BaseModel):
    user_ids: list[int] = Field([])


class TeamResponseOutSchema(BaseModel):
    id: int
    name: str
    description: str | None
