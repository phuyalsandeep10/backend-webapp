from pydantic import BaseModel, Field, EmailStr


class TeamDto(BaseModel):
    name: str = Field(..., max_length=250)
    description: str | None = Field(None, max_length=300)


class TeamMemberDto(BaseModel):
    user_ids: list[int] = Field([])
