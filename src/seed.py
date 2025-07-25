import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import src.models
from src.common.utils import hash_password
from src.modules.auth.models import User
from src.modules.organizations.models import Organization, OrganizationMember
from src.modules.ticket.models import Priority, TicketStatus

# default data
priorities = [
    {"name": "Critical", "level": 0, "color": "#ffffff", "organization_id": 1},
    {"name": "High", "level": 1, "color": "#ffffff", "organization_id": 1},
    {"name": "Medium", "level": 2, "color": "#ffffff", "organization_id": 1},
    {"name": "Low", "level": 3, "color": "#ffffff", "organization_id": 1},
    {"name": "Trivial", "level": 4, "color": "#ffffff", "organization_id": 1},
]

status = [
    {"name": "Open", "color": "#ffffff", "organization_id": 1},
    {"name": "Pending", "color": "#ffffff", "organization_id": 1},
    {"name": "Closed", "color": "#ffffff", "organization_id": 1},
]


async def user_seed_dummy():
    # checking if test user exists or not
    test_exist = await User.find_one(where={"email": "test@gmail.com"})
    data = {"email": "test@gmail.com", "password": "test12345", "name": "test"}

    if not test_exist:
        user = await User.create(
            email=data["email"],
            name=data["name"],
            password=hash_password(data["password"]),
        )
        print("Test User created")
    else:
        print("Test User already exists")


async def organization_seed_dummy():

    record = await Organization.find_one(
        where={
            "name": {"mode": "insensitive", "value": "test"},
        }
    )
    if not record:
        organization = await Organization.create(
            name="test",
            description="test description",
            slug="test".lower().replace(" ", "-"),  # Simple slug generation
            logo="test",
            website="test.com",
        )
        print("Organization created")
    else:
        print("Organization already created")


async def organization_user_seed_dummy():
    user = await OrganizationMember.find_one(where={"user_id": 1})
    if not user:
        await OrganizationMember.create(organization_id=1, user_id=1)
        print("User added to organization 1")
    else:
        print("User already added or there is not user with 1 id")


async def priority_seed():
    for i in priorities:
        record = await Priority.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
            }
        )
        if not record:
            await Priority.create(
                name=i["name"],
                level=i["level"],
                color=i["color"],
                organization_id=i["organization_id"],
            )
            print("Priority created")
        else:
            print("Priority already created")


async def status_seed():
    for i in status:
        record = await TicketStatus.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
            }
        )
        if not record:
            await TicketStatus.create(
                name=i["name"],
                color=i["color"],
                organization_id=i["organization_id"],
            )
            print("Status created")
        else:
            print("Status already created")


async def seed_func():
    await organization_seed_dummy()
    await user_seed_dummy()
    await organization_user_seed_dummy()
    await priority_seed()
    await status_seed()


if __name__ == "__main__":
    asyncio.run(seed_func())
