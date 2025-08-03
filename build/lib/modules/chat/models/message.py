from src.common.models import CommonModel
from sqlmodel import Field, Relationship
from typing import Optional,TYPE_CHECKING

if TYPE_CHECKING:
    from src.modules.chat.models.customer import Customer
    from src.modules.auth.models import User



class Message(CommonModel, table=True):
    __tablename__ = "org_messages" #type:ignore
    conversation_id: int = Field(foreign_key="org_conversations.id", nullable=False)
    content: str = Field(max_length=255, index=True)
    customer_id: int = Field(foreign_key="org_customers.id", nullable=False)
    customer: Optional["Customer"] = Relationship(back_populates="messages")
    user_id: int = Field(foreign_key="sys_users.id", nullable=True)
    user: Optional["User"] = Relationship(
        back_populates="messages",
        sa_relationship_kwargs={"foreign_keys": "[Message.user_id]"},
    )

    feedback: str = Field(max_length=255, index=True, nullable=True)

    attachments: list["MessageAttachment"] = Relationship(back_populates="message")




class MessageAttachment(CommonModel, table=True):
    __tablename__ = "org_message_attachments" #type:ignore
    message_id: int = Field(foreign_key="org_messages.id", nullable=False)
    message: Optional["Message"] = Relationship(back_populates="attachments")
    file_name: str = Field(max_length=255)
    file_type: str = Field(max_length=255)  
    # file_size: int = Field(index=True)
    file_url: str = Field(max_length=255)
