from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING, List
import datetime
from src.common.models import CommonModel

if TYPE_CHECKING:
    from src.modules.chat.models.conversation import Conversation
    from src.modules.chat.models.message import Message
    from src.modules.organizations.models import Organization
    from src.modules.ticket.models.ticket import Ticket


class Customer(CommonModel, table=True):
    __tablename__ = "org_customers"  # type:ignore
    name: str = Field(max_length=255, index=True, nullable=True)
    description: str = Field(default=None, max_length=500, nullable=True)
    organization_id: int = Field(foreign_key="sys_organizations.id", nullable=False)
    organization: Optional["Organization"] = Relationship(back_populates="customers")
    conversations: List["Conversation"] = Relationship(back_populates="customer")
    messages: list["Message"] = Relationship(back_populates="customer")

    phone: str = Field(max_length=255, index=True, nullable=True)
    email: str = Field(max_length=255, index=True, nullable=True)

    attributes: dict = Field(default={})

    ip_address: str = Field(max_length=255, index=True, nullable=True)

    is_online: bool = Field(default=False)
    tickets: List["Ticket"] = Relationship(back_populates="customer")


class CustomerVisitLogs(CommonModel, table=True):
    __tablename__ = "org_customer_visit_logs"  # type:ignore
    ip_address: str = Field(max_length=255, index=True, nullable=True)
    latitude: float = Field(nullable=True)
    longitude: float = Field(nullable=True)
    city: str = Field(max_length=255, nullable=True)
    country: str = Field(max_length=255, nullable=True)
    location: str = Field(max_length=300, nullable=True)
    customer_id: int = Field(foreign_key="org_customers.id", nullable=False)
    customer: Optional["Customer"] = Relationship(back_populates="visit_logs")

    device: str = Field(max_length=300, nullable=True)
    os: Optional[str] = Field(max_length=100, nullable=True)
    browser: Optional[str] = Field(max_length=100, nullable=True)
    device_type: Optional[str] = Field(
        max_length=50, nullable=True, description="e.g. desktop, mobile, tablet"
    )
    user_agent: Optional[str] = Field(max_length=512, nullable=True)

    referral_from: str = Field(
        max_length=300, nullable=True
    )  # for example: from facebook, google search, chatgpt, etc.

    join_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    left_at: Optional[datetime] = Field(default=None, nullable=True)
    city: str = Field(max_length=255, index=True, nullable=True)
    country: str = Field(max_length=255, index=True, nullable=True)

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": f"{self.city}, {self.country}",
        }
