from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, Session, SQLModel, select

from src.common.models import CommonModel
from src.db.config import async_session

# from src.modules.auth.models import User
from src.enums import InvitationStatus

if TYPE_CHECKING:
    from src.modules.auth.models import User
    from src.modules.chat.models.conversation import Conversation
    from src.modules.chat.models.customer import Customer
    from src.modules.ticket.models.priority import TicketPriority
    from src.modules.ticket.models.status import TicketStatus
    from src.modules.ticket.models.ticket import Ticket
    from src.modules.common.models import Country, Timezone #type:ignore


class Organization(CommonModel, table=True):
    __tablename__ = "sys_organizations"  # type:ignore
    name: str = Field(max_length=255, index=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    slug: str = Field(default=None, max_length=255, nullable=False, index=True)

    domain: str = Field(default=None, max_length=255)
    logo: str = Field(default=None, max_length=255, nullable=True)

    identifier: str = Field(default=None, max_length=255, nullable=True)

    contact_phone: str = Field(default=None, max_length=10, nullable=True)
    contact_email: str = Field(
        default=None,
    )

    country_id: Optional[int] = Field(default=None, foreign_key="sys_countries.id")
    timezone_id: Optional[int] = Field(default=None, foreign_key="sys_timezones.id")

    twitter_username: Optional[str] = Field(default=None, max_length=255, nullable=True)
    facebook_username: Optional[str] = Field(default=None, max_length=255)
    whatsapp_number: Optional[str] = Field(default=None, max_length=255)
    telegram_username: Optional[str] = Field(default=None, max_length=255)

    contact_dial_code: Optional[str] = Field(default=None, max_length=10, nullable=True)

    address: Optional[str] = Field(default=None, max_length=255)

    members: list["OrganizationMember"] = Relationship(back_populates="organization")
    conversations: list["Conversation"] = Relationship(back_populates="organization")
    customers: list["Customer"] = Relationship(back_populates="organization")

    country: Optional["Country"] = Relationship()
    timezone: Optional["Timezone"] = Relationship()
    
    ticket_priorities: List["TicketPriority"] = Relationship(
        back_populates="organization"
    )

    ticket_status: List["TicketStatus"] = Relationship(back_populates="organizations")
    tickets: List["Ticket"] = Relationship(back_populates="organization")
    purpose: str = Field(default=None, max_length=250, nullable=True)

    owner_id: int = Field(foreign_key="sys_users.id", nullable=False)
    owner: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Organization.owner_id]"}
    )

    @classmethod
    async def get_orgs_by_user_id(cls, user_id: int):
        async with async_session() as session:
            statement = (
                select(cls)
                .join(OrganizationMember)
                .where(OrganizationMember.user_id == user_id)
            )
            result = await session.execute(statement)
            return list(result.scalars().all())


class OrganizationRole(CommonModel, table=True):
    __tablename__ = "org_roles"  # type:ignore
    name: str = Field(max_length=255, index=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    identifier: str = Field(default=None, max_length=500, nullable=False, index=True)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    permissions: list[str] = Field(default=[], sa_column=sa.Column(sa.JSON))

    member_roles: list["OrganizationMemberRole"] = Relationship(back_populates="role")


class OrganizationMember(CommonModel, table=True):
    __tablename__ = "org_members"  # type:ignore
    user_id: int = Field(foreign_key="sys_users.id", nullable=False)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)

    organization: Optional[Organization] = Relationship(back_populates="members")
    user: Optional["User"] = Relationship(
        back_populates="members",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.user_id]"},
    )

    member_roles: List["OrganizationMemberRole"] = Relationship(back_populates="member")


class OrganizationMemberRole(CommonModel, table=True):
    __tablename__ = "org_member_roles"  # type:ignore
    member_id: int = Field(foreign_key="org_members.id", nullable=False)
    role_id: int = Field(foreign_key="org_roles.id", nullable=False)
    member: Optional[OrganizationMember] = Relationship(back_populates="member_roles")
    role: Optional[OrganizationRole] = Relationship(back_populates="member_roles")


class OrganizationInvitation(CommonModel, table=True):
    __tablename__ = "org_invitations"  # type:ignore
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
