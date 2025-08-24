from src.seed.organization import organization_seed_dummy, organization_user_seed_dummy
from src.seed.user import user_seed_dummy

from src.seed.team import department_team_seed_dummy
import asyncio


async def seed_func():
    await user_seed_dummy()
    await organization_seed_dummy()
    await organization_user_seed_dummy()
    await department_team_seed_dummy()
    # await priority_seed()
    # await status_seed()
    # await sla_seed_dummy()


print(f"__name__ {__name__}")
if __name__ == "__main__":
    print("Running seed main script")
    asyncio.run(seed_func())
