import asyncio
from sqlmodel import select
from src.modules.staff_management.models.permission_group import PermissionGroup
from src.db import async_session  


async def permission_group_seed():
    group_names = [
        "Setting",
        "Channels",
        "inbox & Contact",
        "Analytics",
        "Section Access",
    ]

    async with async_session() as session:
        allpermission = select(PermissionGroup).where(
            PermissionGroup.name.in_(group_names)
        )
        result = await session.execute(allpermission)
        existing_groups = {group.name for group in result.scalars().all()}

        new_groups = []
        for name in group_names:
            if name not in existing_groups:
                new_groups.append(PermissionGroup(name=name))

        if new_groups:
            session.add_all(new_groups)
            await session.commit()
            print(f"Created PermissionGroups: {[g.name for g in new_groups]}")
        else:
            print("All permission groups already exist.")


if __name__ == "__main__":
    asyncio.run(permission_group_seed())
