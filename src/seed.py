import asyncio
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import src.models
from src.common.utils import hash_password
from src.modules.auth.models import User
from src.modules.organizations.models import Organization, OrganizationMember
from src.modules.team.models import Team
from src.modules.ticket.models import Priority, TicketStatus
from src.modules.ticket.models.sla import SLA

# default data
priorities = [
    {"name": "Critical", "level": 0, "color": "#ffffff", "organization_id": 1},
    {"name": "High", "level": 1, "color": "#ffffff", "organization_id": 1},
    {"name": "Medium", "level": 2, "color": "#ffffff", "organization_id": 1},
    {"name": "Low", "level": 3, "color": "#ffffff", "organization_id": 1},
    {"name": "Trivial", "level": 4, "color": "#ffffff", "organization_id": 1},
]
priorities2 = [
    {"name": "High", "level": 0, "color": "#ffffff", "organization_id": 2},
    {"name": "Medium", "level": 1, "color": "#ffffff", "organization_id": 2},
    {"name": "Low", "level": 2, "color": "#ffffff", "organization_id": 2},
]

status = [
    {"name": "Open", "color": "#ffffff", "organization_id": 1},
    {"name": "Pending", "color": "#ffffff", "organization_id": 1},
    {"name": "Closed", "color": "#ffffff", "organization_id": 1},
]
status2 = [
    {"name": "Open", "color": "#ffffff", "organization_id": 2},
    {"name": "In-Progress", "color": "#ffffff", "organization_id": 2},
    {"name": "Pending", "color": "#ffffff", "organization_id": 2},
    {"name": "Closed", "color": "#ffffff", "organization_id": 2},
]


async def user_seed_dummy():
    # checking if test user exists or not
    test_exist = await User.find_one(where={"email": "test@gmail.com"})
    test_exist2 = await User.find_one(where={"email": "test2@gmail.com"})
    data = {"email": "test@gmail.com", "password": "test12345", "name": "test"}
    data2 = {"email": "test2@gmail.com", "password": "test12345", "name": "test2"}

    if not test_exist:
        user = await User.create(
            email=data["email"],
            name=data["name"],
            password=hash_password(data["password"]),
        )

        await User.update(
            user.id,
            email_verified_at=datetime.utcnow(),
            attributes={"organization_id": 1},
        )
        print("Test User1 created")
    else:
        print("Test User1 already exists")

    if not test_exist2:
        user = await User.create(
            email=data2["email"],
            name=data2["name"],
            password=hash_password(data2["password"]),
        )

        await User.update(
            user.id,
            email_verified_at=datetime.utcnow(),
            attributes={"organization_id": 2},
        )
        print("Test User2 created")
    else:
        print("Test User2 already exists")


async def organization_seed_dummy():

    record = await Organization.find_one(
        where={
            "name": {"mode": "insensitive", "value": "test"},
        }
    )
    record2 = await Organization.find_one(
        where={
            "name": {"mode": "insensitive", "value": "test2"},
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

        print("Organization 1 created")
    else:
        print("Organization 1 already created")

    if not record2:
        organization = await Organization.create(
            name="test2",
            description="test2 description",
            slug="test2".lower().replace(" ", "-"),  # Simple slug generation
            logo="test2",
            website="test2.com",
        )

        print("Organization 2 created")
    else:
        print("Organization 2 already created")


async def organization_user_seed_dummy():
    user = await OrganizationMember.find_one(where={"user_id": 1})
    user2 = await OrganizationMember.find_one(where={"user_id": 2})
    if not user:
        await OrganizationMember.create(organization_id=1, user_id=1)

        print("User added to organization 1")
    else:
        print("User already added or there is not user with 1 id")
    if not user2:
        await OrganizationMember.create(organization_id=2, user_id=2)

        print("User added to organization 2")
    else:
        print("User already added or there is not user with 2 id")


async def department_team_seed_dummy():

    record = await Team.find_one(
        where={"name": {"mode": "insensitive", "value": "test"}}
    )
    record2 = await Team.find_one(
        where={"name": {"mode": "insensitive", "value": "test2"}}
    )

    if not record:

        await Team.create(
            name="test",
            description="THis is test team",
            organization_id=1,
        )
        print("Test Team 1 created")
    else:
        print("Test team 1 already exists")

    if not record2:

        await Team.create(
            name="test2",
            description="THis is test team2",
            organization_id=2,
        )
        print("Test Team 2 created")
    else:
        print("Test team 2 already exists")


async def priority_seed():
    for i in priorities:
        record = await Priority.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await Priority.create(
                name=i["name"],
                level=i["level"],
                color=i["color"],
                organization_id=i["organization_id"],
            )
            print("Priority 1 created")
        else:
            print("Priority 1 already created")

    for i in priorities2:
        record = await Priority.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await Priority.create(
                name=i["name"],
                level=i["level"],
                color=i["color"],
                organization_id=i["organization_id"],
            )
            print("Priority2 created")
        else:
            print("Priority2 already created")


async def status_seed():
    for i in status:
        record = await TicketStatus.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await TicketStatus.create(
                name=i["name"],
                color=i["color"],
                organization_id=i["organization_id"],
            )
            print("Status 1 created")
        else:
            print("Status 1 already created")

    for i in status2:
        record = await TicketStatus.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await TicketStatus.create(
                name=i["name"],
                color=i["color"],
                organization_id=i["organization_id"],
            )
            print("Status 2 created")
        else:
            print("Status 2 already created")


async def sla_seed_dummy():
    record = await SLA.find_one(
        where={
            "name": {"mode": "insensitive", "value": "test_sla"},
        }
    )
    record2 = await SLA.find_one(
        where={
            "name": {"mode": "insensitive", "value": "test_sla2"},
        }
    )
    if not record:
        await SLA.create(
            name="test_sla",
            response_time=18000,  # 5 hours
            resolution_time=432000,  # 5 days
            organization_id=1,
            issued_by=1,
        )
        print("Test SLA 1 has been created")
    else:
        print("Test SLA 1 already exists")

    if not record2:
        await SLA.create(
            name="test_sla2",
            response_time=18000,  # 5 hours
            resolution_time=432000,  # 5 days
            organization_id=1,
            issued_by=1,
        )
        print("Test SLA 2 has been created")
    else:
        print("Test SLA 2 already exists")


async def seed_func():
    await organization_seed_dummy()
    await user_seed_dummy()
    await organization_user_seed_dummy()
    await department_team_seed_dummy()
    await priority_seed()
    await status_seed()
    await sla_seed_dummy()


if __name__ == "__main__":
    asyncio.run(seed_func())
