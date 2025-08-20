
from pydantic import BaseModel
from typing import Optional
# from typing import datetime
class CustomerSchema(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    created_at: str
    updated_at: str
    
class ConversationSchema(BaseModel):
    id: int
    customer_id: int
    name: str
    created_at: str
    updated_at: str
    attributes: dict
    is_resolved: bool
    customer: CustomerSchema


class MessageAttachment(BaseModel):
    id: int
    message_id: int
    file_name: str
    file_size: int
    file_type: str
    created_at: str
    updated_at: str

class MessageSchema(BaseModel):
    
    content: str
    customer_id:Optional[int] = None
    attachments: Optional[list[MessageAttachment]]=[]
