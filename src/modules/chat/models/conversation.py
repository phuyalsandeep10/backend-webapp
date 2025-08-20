from typing import TYPE_CHECKING, List, Optional,Any

from sqlmodel import Field, Relationship
from sqlalchemy import Column,JSON
from sqlalchemy.orm import joinedload

from src.common.models import CommonModel
from src.db.config import async_session
from sqlmodel import select


if TYPE_CHECKING:
    from src.modules.auth.models import User
    from src.modules.chat.models.customer import Customer
    from src.modules.organizations.models import Organization


class Conversation(CommonModel, table=True):
    __tablename__ = "org_conversations"  # type:ignore
    name: str = Field(max_length=255, index=True, nullable=True)
    
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    customer_id: int = Field(foreign_key="org_customers.id", nullable=False)

    organization: Optional["Organization"] = Relationship(
        back_populates="conversations"
    )

    customer: Optional["Customer"] = Relationship(back_populates="conversations")
    members: List["ConversationMember"] = Relationship(back_populates="conversation")
    attributes: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    is_resolved: bool = Field(default=False)




    @classmethod
    async def get_list(cls,organization_id:int):
        async with async_session() as session:
            statement = select(cls).filter(cls.organization_id == organization_id).options(joinedload(cls.members).joinedload(ConversationMember.user),joinedload(cls.customer))
            results = await session.execute(statement)
            conversations = results.scalars().unique().all()
            return conversations
    


           
async def get_conversation_list(organization_id:int):
    conversations = await Conversation.get_list(organization_id)
    new_list = []
    # new_conversations = [conv.to_json() for conv in conversations]
    for conversation in conversations:
        data = {
            "id":conversation.id,
            "name":conversation.name,
            "customer_id":conversation.customer_id,
            "customer":conversation.customer.to_json(),
            "organization_id":conversation.organization_id, 
            "members":[],
            "created_at":conversation.created_at.isoformat(),
            "updated_at":conversation.updated_at.isoformat(),
        }
        members = []
        for member in conversation.members:
            record = {
                "id":member.id,
                "conversation_id":member.conversation_id,
                "user_id":member.user_id,
                "user":member.user.to_json(),
  
            }
            members.append(record)
        data["members"] = members
        new_list.append(data)
    return new_list


class ConversationMember(CommonModel, table=True):
    __tablename__ = "org_conversation_members"  # type:ignore
    user_id: int = Field(foreign_key="sys_users.id", nullable=False)
    conversation_id: int = Field(foreign_key="org_conversations.id", nullable=False)
    conversation: Optional["Conversation"] = Relationship(back_populates="members")

    user: Optional["User"] = Relationship(
        back_populates="conversation_members",
        sa_relationship_kwargs={"foreign_keys": "[ConversationMember.user_id]"},
    )

    created_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ConversationMember.created_by_id]"}
    )
