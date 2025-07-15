from typing import Optional
from sqlmodel import Field, Relationship
from datetime import datetime
import sqlalchemy as sa
from src.common.models import BaseModel
from src.modules.organizations.models import OrganizationMember
from src.modules.team.models import TeamMember



class User(BaseModel, table=True):
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    image: Optional[str] = None
    mobile: Optional[str] = Field(default=None, unique=True)
    password: str = Field(default='', min_length=8, max_length=128)
    is_active: bool = Field(default=True)
    email_verified_at: datetime = Field(
        default=None,
        nullable=True,
    )
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    attributes: Optional[dict] = Field(default=None, sa_column=sa.Column(sa.JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    members: list[OrganizationMember] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[OrganizationMember.user_id]"},
    )

    team_members: list["TeamMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[TeamMember.user_id]"},
    )
    # messages: list[Message] = Relationship(
    #     back_populates="user",
    #     sa_relationship_kwargs={"foreign_keys": "[Message.user_id]"},
    # )
    # conversations: list["ConversationMember"] = Relationship(
    #     back_populates="user",
    #     sa_relationship_kwargs={"foreign_keys": "[ConversationMember.user_id]"},
    # )


    class Config:
        table_name = 'sys_users'



class RefreshToken(BaseModel, table=True):
    user_id: int = Field(foreign_key="sys_users.id")
    token: str = Field(unique=True, index=True)
    active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(nullable=False)

    class Config:
        table_name = 'refresh_tokens'


class EmailVerification(BaseModel, table=True):
    user_id: int = Field(foreign_key="sys_users.id")
    token: str = Field(unique=True, index=True)
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(
        nullable=True
    )  # Use appropriate datetime type if needed
    type: str = Field(default="email_verification")

    class Config:
        table_name = 'email_verifications'
