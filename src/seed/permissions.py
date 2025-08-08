from src.models import Permissions


async def permission_seed_dummy_group1():
    permission_names = [
        "Canned Response",
        "Workflows",
        "Tags & Properties",
        "Billings",
        "Project preferences",
        "Project reports",
        "Service Level Agreement",
    ]

    # all the above permssion belongs to per_group 1
    group_id = 1

    for name in permission_names:
        existing = await Permissions.find_one(
            where={"name": {"mode": "insensitive", "value": name}}
        )
        if not existing:
            await Permissions.create(name=name, group_id=group_id)
            print(f"Permission '{name}' created with group_id {group_id}")
        else:
            print(f"Permission '{name}' already exists (group_id not updated)")


async def permission_seed_dummy_group2():
    permission_names = [
        "User Management",
        "Access Control",
        "Notification Settings",
        "Audit Logs",
        "Data Export",
        "API Access",
        "Billing Reports",
    ]

    group_id = 2

    for name in permission_names:
        existing = await Permissions.find_one(
            where={"name": {"mode": "insensitive", "value": name}}
        )
        if not existing:
            await Permissions.create(name=name, group_id=group_id)
            print(f"Permission '{name}' created with group_id {group_id}")
        else:
            print(f"Permission '{name}' already exists (group_id not updated)")
