from pydantic import BaseModel, Field


class PermissionDto(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=250)
    identifier: str = Field(..., max_length=255)
