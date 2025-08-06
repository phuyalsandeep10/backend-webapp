# This file imports all models to ensure they are properly registered with SQLAlchemy
# Import order is important to avoid circular dependencies

# First, import base models and common dependencies
from src.common.models import CommonModel

# Import auth models first (they have no dependencies on other modules)
from src.modules.auth.models import User
from src.modules.chat.models.conversation import Conversation, ConversationMember

# Import chat models
<<<<<<< HEAD
from src.modules.chat.models.customer import Customer
=======

from src.modules.chat.models.customer import Customer, CustomerVisitLogs

>>>>>>> 1a107ebf6153bf73854e8a942397333a9cffe4f6
from src.modules.chat.models.message import Message, MessageAttachment

# Import organization models
from src.modules.organizations.models import (
    Organization,
    OrganizationInvitation,
    OrganizationMember,
    OrganizationMemberRole,
    OrganizationRole,
)

from src.modules.staff_managemet.models import (
    Permissions,
    PermissionGroup,
    RolePermission,
)

# Import team models
from src.modules.team.models import Team, TeamMember
from src.modules.ticket.models.priority import TicketPriority
from src.modules.ticket.models.sla import TicketSLA
from src.modules.ticket.models.status import TicketStatus
from src.modules.ticket.models.ticket import Ticket, TicketAlert, TicketAssigneesLink

# Import admin models
# from src.modules.admin.models import Admin

# This ensures all models are imported and registered with SQLAlchemy
__all__ = [
    "CommonModel",
    "User",
    "Organization",
    "OrganizationRole",
    "OrganizationMember",
    "OrganizationMemberRole",
    "OrganizationInvitation",
    "Customer",
    "Conversation",
    "ConversationMember",
    "Message",
    "MessageAttachment",
    "Team",
    "TeamMember",
    "Ticket",
    "TicketStatus",
    "TicketAssigneesLink",
    "TicketAlert",
    "TicketPriority",
    "TicketSLA",
<<<<<<< HEAD
    # "Admin",
    Permissions,
    PermissionGroup,
    RolePermission,
=======
    "CustomerVisitLogs",
    # "Admin"
>>>>>>> 1a107ebf6153bf73854e8a942397333a9cffe4f6
]
