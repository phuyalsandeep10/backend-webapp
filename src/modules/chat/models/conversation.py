from sqlalchemy.orm import foreign
from src.common.models import CommonModel
from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from src.modules.organizations.models import Organization
    from src.modules.auth.models import User

class Conversation(CommonModel, table=True):
    __tablename__ = "org_conversations" #type:ignore
    name: str = Field(max_length=255, index=True, nullable=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    customer_id: int = Field(foreign_key="org_customers.id", nullable=False)
    organization: Optional["Organization"] = Relationship( 
        back_populates="conversations"
    )
    customer: Optional["Customer"] = Relationship(back_populates="conversations") #type:ignore
    members: list["ConversationMember"] = Relationship(back_populates="conversation")
    ip_address: str = Field(max_length=255, index=True, nullable=True)


class ConversationMember(CommonModel, table=True):
    __tablename__ = "org_conversation_members" #type:ignore
    user_id: int = Field(foreign_key="sys_users.id", nullable=False)
    conversation_id: int = Field(foreign_key="org_conversations.id", nullable=False)
    conversation: Optional["Conversation"] = Relationship(back_populates="members")
   
    user: Optional["User"] = Relationship(
        back_populates="conversation_members",
        sa_relationship_kwargs={"foreign_keys": "[ConversationMember.user_id]"}
    )
    created_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ConversationMember.created_by_id]"}
    )
