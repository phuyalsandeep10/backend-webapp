from sqlmodel import Column, Field, ForeignKey, Relationship, SQLModel
from src.common.models import BaseModel


class Timezone(BaseModel, table=True):
    __tablename__ = "sys_timezones"

    name: str = Field(nullable=False) #IANA timezone name
    display_name: str = Field(nullable=False)
    country_id: int = Field(foreign_key="sys_countries.id")

    country: "Country" = Relationship(back_populates="timezones")

