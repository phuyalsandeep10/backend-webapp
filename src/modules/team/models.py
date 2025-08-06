from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from src.common.models import CommonModel

if TYPE_CHECKING:
    from src.modules.auth.models import User
    from src.modules.ticket.models.ticket import Ticket


class Team(CommonModel, table=True):
    __tablename__ = "org_teams"  # type:ignore

    name: str = Field(..., max_length=255)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    description: str | None = Field(None, max_length=300)

    tickets: List["Ticket"] = Relationship(back_populates="department")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


class TeamMember(CommonModel, table=True):
    __tablename__ = "org_team_members"  # type:ignore
    team_id: int = Field(foreign_key="org_teams.id", nullable=False)
    user_id: int = Field(foreign_key="sys_users.id", nullable=False)

    user: Optional["User"] = Relationship(
        back_populates="team_members",
        sa_relationship_kwargs={"foreign_keys": "[TeamMember.user_id]"},
    )

    def to_dict(self):

        return {"id": self.id, "user": self.user.to_dict()}
