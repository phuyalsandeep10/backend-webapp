from src.modules.staff_managemet.models.permission_group import PermissionGroup
from src.modules.staff_managemet.models.permissions import Permissions


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


async def permission_seed_dummy():
    group_names = [
        "inbox",
        "ticket",
        "ticket_priority",
        "ticket_status",
        "sla",
    ]

    for name in group_names:
        existing = await Permissions.find_one(
            where={"name": {"mode": "insensitive", "value": name}}
        )
        if not existing:
            await Permissions.create(name=name)
            print(f"Permission  '{name}' created")
        else:
            print(f"Permission  '{name}' already exists")
