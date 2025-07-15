from src.common.models import CommonModel
from sqlmodel import Field, Relationship, SQLModel, Session, select
from typing import Optional


class Team(CommonModel, table=True):
    __tablename__ = "org_teams"

    name: str = Field(..., max_length=255)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    description: str | None = Field(None, max_length=300)


class TeamMember(CommonModel, table=True):
    __tablename__ = "org_team_members"
    team_id: int = Field(foreign_key="org_teams.id", nullable=False)
    user_id: int = Field(foreign_key="sys_users.id", nullable=False)

    user: Optional["User"] = Relationship(
        back_populates="team_members",
        sa_relationship_kwargs={"foreign_keys": "[TeamMember.user_id]"},
    )
