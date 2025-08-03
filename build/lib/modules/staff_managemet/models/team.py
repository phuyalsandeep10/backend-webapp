from src.common.models import CommonModel
from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING, List, Optional

class Team(CommonModel, table=True):
    __tablename__= "org_teams"  # type:ignore
    name: str = Field(max_length=255, index=True, nullable=False)
    