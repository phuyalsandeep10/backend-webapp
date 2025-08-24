from pydantic import BaseModel, Field


class TeamSchema(BaseModel):
    name: str = Field(..., max_length=250)
    description: str | None = Field(None, max_length=300)


class TeamMemberSchema(BaseModel):
    user_ids: list[int] = Field([])
