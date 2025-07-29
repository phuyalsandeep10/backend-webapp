from enum import Enum


class PriorityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class TicketStatusEnum(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"


class TicketEmailTypeEnum(str, Enum):
    EMAIL_RESPONSE = "email_response"
    EMAIL_SLA_BREACH = "email_sla_breach"
    EMAIL_TICKET_SOLVED = "email_ticket_solved"


class WarningLevelEnum(str, Enum):
    WARNING_75 = 75
    WARNING_90 = 90
    WARNING_100 = 100


class TicketAlertTypeEnum(str, Enum):
    RESPONSE = "response"
    RESOLUTION = "resolution"
