from src.models import PermissionGroup


async def permission_group_seed_dummy():
    group_names = [
        "Setting",
        "Channels",
        "Inbox & Contact",
        "Analystics",
        "Section Access",
    ]

    for name in group_names:
        existing = await PermissionGroup.find_one(
            where={"name": {"mode": "insensitive", "value": name}}
        )
        if not existing:
            await PermissionGroup.create(name=name)
            print(f"Permission group '{name}' created")
        else:
            print(f"Permission group '{name}' already exists")