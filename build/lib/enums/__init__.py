from enum import Enum
from .organization import InvitationStatus

class ProviderEnum(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"
