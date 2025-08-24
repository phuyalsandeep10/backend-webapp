from typing import Optional, List
from src.common.models import BaseModel
from sqlmodel import Field, Relationship


class Country(BaseModel, table=True):
    __tablename__ = "sys_countries"

    name: str = Field(nullable=False)
    iso_code_2: str = Field(max_length=2, nullable=False)  # "NP", "US"
    iso_code_3: str = Field(max_length=3, nullable=False)  # "NPL", "USA"
    phone_code: Optional[str] = None

    timezones: List["Timezone"] = Relationship(back_populates="country")
