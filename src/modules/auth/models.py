from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship

from src.common.models import BaseModel
from src.modules.chat.models.conversation import ConversationMember
from src.modules.chat.models.message import Message
from src.modules.organizations.models import OrganizationMember
from src.modules.team.models import TeamMember
from src.modules.ticket.models.ticket import Ticket, TicketAssigneesLink


class User(BaseModel, table=True):
    __tablename__ = "sys_users"  # type:ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_2fa_verified = False

    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    image: Optional[str] = None
    mobile: Optional[str] = Field(default=None, unique=True)
    password: str = Field(default="", min_length=8, max_length=128)
    is_active: bool = Field(default=True)
    two_fa_enabled: bool = Field(default=False)
    two_fa_secret: str = Field(default=None)
    two_fa_auth_url: str = Field(default=None)

    email_verified_at: datetime = Field(
        default=None,
        nullable=True,
    )

    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    attributes: Optional[dict] = Field(default=None, sa_column=sa.Column(sa.JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    members: List["OrganizationMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.user_id]"},
    )

    team_members: List["TeamMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[TeamMember.user_id]"},
    )

    messages: List["Message"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Message.user_id]"},
    )

    conversation_members: List["ConversationMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[ConversationMember.user_id]"},
    )
    issued_tickets: List[Ticket] = Relationship(back_populates="issued_by")

    assigned_tickets: List[Ticket] = Relationship(
        back_populates="assignees", link_model=TicketAssigneesLink
    )

    def to_dict(self):
        return {"email": self.email, "name": self.name}

    @property
    def is_2fa_verified(self):
        return getattr(self, "_is_2fa_verified", False)

    @is_2fa_verified.setter
    def is_2fa_verified(self, value):
        self._is_2fa_verified = value


class RefreshToken(BaseModel, table=True):
    __tablename__ = "refresh_tokens"  # type:ignore
    user_id: int = Field(foreign_key="sys_users.id")
    token: str = Field(unique=True, index=True)
    active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(nullable=False)


class EmailVerification(BaseModel, table=True):
    __tablename__ = "email_verifications"  # type:ignore
    user_id: int = Field(foreign_key="sys_users.id")
    token: str = Field(unique=True, index=True)
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(
        nullable=True
    )  # Use appropriate datetime type if needed
    type: str = Field(default="email_verification")
