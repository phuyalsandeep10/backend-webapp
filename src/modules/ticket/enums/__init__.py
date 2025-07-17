from enum import Enum


class PriorityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class StatusEnum(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"
