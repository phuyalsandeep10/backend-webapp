from enum import Enum, IntEnum


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
    REOPENED = "reopened"


class TicketEmailTypeEnum(str, Enum):
    EMAIL_RESPONSE = "email_response"
    EMAIL_SLA_BREACH = "email_sla_breach"
    EMAIL_TICKET_SOLVED = "email_ticket_solved"


class WarningLevelEnum(IntEnum):
    WARNING_75 = 75
    WARNING_90 = 90
    WARNING_100 = 100


class TicketAlertTypeEnum(str, Enum):
    RESPONSE = "response"
    RESOLUTION = "resolution"


class TicketLogActionEnum(str, Enum):
    TICKET_CREATED = "ticket_created"
    TICKET_UPDATED = "ticket_created"
    TICKET_DELETED = "ticket_created"
    STATUS_CHANGED = "ticket_created"
    ASSIGNEE_CHANGED = "ticket_created"
    PRIORITY_CHANGED = "ticket_created"
    CONFIRMATION_EMAIL_SENT = "confirmation_email_sent"


class TicketLogEntityEnum(str, Enum):
    TICKET = "ticket"
    TICKET_SLA = "ticket_sla"
    TICKET_STATUS = "ticket_status"
    TICKET_PRIORITY = "ticket_priority"
