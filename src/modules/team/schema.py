from pydantic import BaseModel, EmailStr, Field

from src.modules.auth.schema import UserOutSchema


class TeamSchema(BaseModel):
    name: str = Field(..., max_length=250)
    description: str | None = Field(None, max_length=300)


class TeamMemberSchema(BaseModel):
    user_ids: list[int] = Field([])


class TeamMemberOutSchema(BaseModel):
    team_id: int
    user: UserOutSchema
