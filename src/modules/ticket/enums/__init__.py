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
    TICKET_UPDATED = "ticket_updated"
    TICKET_DELETED = "ticket_hard_deleted"
    TICKET_SOFT_DELETED = "ticket_soft_deleted"
    TICKET_CONFIRMED = "ticket_confirmed"
    STATUS_CREATED = "ticket_status_created"
    STATUS_DELETED = "ticket_status_deleted"
    STATUS_UPDATED = "ticket_status_updated"
    ASSIGNEE_CHANGED = "ticket_assignee_changed"
    PRIORITY_CREATED = "ticket_priority_created"
    PRIORITY_UPDATED = "ticket_priority_updated"
    PRIORITY_DELETED = "ticket_priority_deleted"
    TICKET_SLA_CREATED = "ticket_sla_created"
    TICKET_SLA_UPDATED = "ticket_sla_updated"
    TICKET_SLA_DELETED = "ticket_sla_deleted"
    CONFIRMATION_EMAIL_SENT = "confirmation_email_sent"
    CONFIRMATION_EMAIL_SENT_FAILED = "confirmation_email_sent_failed"
    SLA_BREACH_EMAIL_SENT = "ticket_sla_breach_email_sent"
    EMAIL_SENT_FAILED = "ticket_email_sent_failed"


class TicketLogEntityEnum(str, Enum):
    TICKET = "ticket"
    TICKET_SLA = "ticket_sla"
    TICKET_STATUS = "ticket_status"
    TICKET_PRIORITY = "ticket_priority"
