from src.models import Permissions


async def permission_seed_dummy():
    group_names = [
        "Canned Response",
        "Workflows",
        "Tags & Properties",
        "Billings",
        "Project preferences",
        "Project reports",
        "Service Level Agreement",
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
