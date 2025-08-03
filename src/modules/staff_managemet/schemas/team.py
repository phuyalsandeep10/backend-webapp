from pydantic import BaseModel, Field, EmailStr
from typing import List

class TeamCreateSchema(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the Team")

