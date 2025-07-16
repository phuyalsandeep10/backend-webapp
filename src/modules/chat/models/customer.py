from src.common.models import CommonModel
from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING,List

if TYPE_CHECKING:
    from src.modules.organizations.models import Organization
    from src.modules.chat.models.conversation import Conversation
    from src.modules.chat.models.message import Message


class Customer(CommonModel, table=True):
    __tablename__ = "org_customers" #type:ignore
    name: str = Field(max_length=255, index=True, nullable=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    organization: Optional["Organization"] = Relationship(back_populates="customers")
    conversations: List["Conversation"] = Relationship(back_populates="customer")
    messages: list["Message"] = Relationship(back_populates="customer")

    phone: str = Field(max_length=255, index=True, nullable=True)
    email: str = Field(max_length=255, index=True, nullable=True)

    ip_address: str = Field(max_length=255, index=True, nullable=True)
    latitude: float = Field(nullable=True)
    longitude: float = Field(nullable=True)
    city: str = Field(max_length=255, index=True, nullable=True)
    country: str = Field(max_length=255, index=True, nullable=True)
