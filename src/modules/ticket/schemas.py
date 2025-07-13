from pydantic import BaseModel

from src.modules.ticket.enums.enums import PriorityEnum, StatusEnum


class CreateTicketSchema(BaseModel):
    title: str
    description: str
    priority: PriorityEnum = PriorityEnum.MEDIUM
    status: StatusEnum = StatusEnum.OPEN
    issued_by: int
    sla_id: int
    contact_id: int
