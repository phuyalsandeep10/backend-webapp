from src.common.models import CommonModel
from sqlmodel import Field, Relationship, SQLModel, Session, select
from typing import Optional

from src.db.config import async_session
import sqlalchemy as sa
# from src.modules.auth.models import User
from src.enums import InvitationStatus
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.modules.auth.models import User
class Organization(CommonModel, table=True):
    name: str = Field(max_length=255, index=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    slug: str = Field(default=None, max_length=255, nullable=False, index=True)
    logo: str = Field(default=None, max_length=255, nullable=True)
    website: str = Field(default=None, max_length=255, nullable=True)
    members: list["OrganizationMember"] = Relationship(back_populates="organization")
    conversations: list["Conversation"] = Relationship(back_populates="organization")
    customers: list["Customer"] = Relationship(back_populates="organization")
    user: "User" = Relationship(back_populates="members")

    @classmethod
    async def get_orgs_by_user_id(cls, user_id: int):
        async with async_session() as session:
            statement = (
                select(cls)
                .join(OrganizationMember)
                .where(OrganizationMember.user_id == user_id)
            )
            return session.exec(statement).all()


class OrganizationRole(CommonModel, table=True):
    __tablename__ = "sys_organization_roles"
    name: str = Field(max_length=255, index=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    identifier: str = Field(default=None, max_length=500, nullable=False, index=True)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    permissions: list[str] = Field(default=[], sa_column=sa.Column(sa.JSON))

    member_roles: list["OrganizationMemberRole"] = Relationship(back_populates="role")


class OrganizationMember(CommonModel, table=True):
    __tablename__ = "sys_organization_members"
    user_id: int = Field(foreign_key="sys_users.id", nullable=False)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)

    is_owner: bool = Field(default=False)
    organization: Optional[Organization] = Relationship(back_populates="members")
    user: Optional["User"] = Relationship(
        back_populates="members",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.user_id]"},
    )

    member_roles: list["OrganizationMemberRole"] = Relationship(back_populates="member")


class OrganizationMemberRole(CommonModel, table=True):
    __tablename__ = "sys_organization_member_roles"
    member_id: int = Field(foreign_key="sys_organization_members.id", nullable=False)
    role_id: int = Field(foreign_key="sys_organization_roles.id", nullable=False)
    member: Optional[OrganizationMember] = Relationship(back_populates="member_roles")
    role: Optional[OrganizationRole] = Relationship(back_populates="member_roles")


class OrganizationInvitation(CommonModel, table=True):
    __tablename__ = "sys_organization_invitations"
    email: str = Field(max_length=255, index=True)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)

    invited_by_id: int = Field(foreign_key="sys_users.id", nullable=False)
    status: str = Field(default=InvitationStatus.PENDING, max_length=50, nullable=False)

    role_ids: list[int] = Field(default_factory=list, sa_column=sa.Column(sa.JSON))

    invited_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationInvitation.invited_by_id]"
        }
    )
