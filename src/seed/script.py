from src.seed.organization import organization_seed_dummy, organization_user_seed_dummy
from src.seed.user import user_seed_dummy
from src.seed.team import department_team_seed_dummy
from src.seed.ticket import priority_seed, status_seed, sla_seed_dummy
import asyncio
from src.seed.permission_group import permission_group_seed_dummy
from src.seed.permissions import permission_seed_dummy


async def seed_func():

    await user_seed_dummy()
    await organization_seed_dummy()
    await organization_user_seed_dummy()
    await department_team_seed_dummy()
    await permission_group_seed_dummy()
    await permission_seed_dummy()
    # await priority_seed()
    # await status_seed()
    # await sla_seed_dummy()c


print(f"__name__ {__name__}")
if __name__ == "__main__":
    print("Running seed main script")
    asyncio.run(seed_func())
