import asyncio

from src.modules.organizations.models import Organization
from src.modules.ticket.models import Ticket, TicketPriority, TicketSLA, TicketStatus
from src.seed.customer import create_customer_logs_seed, create_customer_seed
from src.seed.organization import organization_seed_dummy, organization_user_seed_dummy
from src.seed.team import department_team_seed_dummy
from src.seed.ticket import priority_seed, sla_seed_dummy, ticket_status_seed
from src.seed.user import user_seed_dummy


async def seed_func():

    await user_seed_dummy()
    await organization_seed_dummy()
    await organization_user_seed_dummy()
    await department_team_seed_dummy()
    await create_customer_seed()
    await create_customer_logs_seed()
    await priority_seed()
    await ticket_status_seed()
    await sla_seed_dummy()


print(f"__name__ {__name__}")
if __name__ == "__main__":
    print("Running seed main script")
    asyncio.run(seed_func())
