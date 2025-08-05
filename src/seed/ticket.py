from src.models import TicketPriority, TicketStatus, TicketSLA

priorities = [
    {
        "name": "Critical",
        "level": 0,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 1,
    },
    {
        "name": "High",
        "level": 1,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 1,
    },
    {
        "name": "Medium",
        "level": 2,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 1,
    },
    {
        "name": "Low",
        "level": 3,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 1,
    },
    {
        "name": "Trivial",
        "level": 4,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 1,
    },
]
priorities2 = [
    {
        "name": "Critical",
        "level": 0,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 2,
    },
    {
        "name": "High",
        "level": 1,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 2,
    },
    {
        "name": "Medium",
        "level": 2,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 2,
    },
    {
        "name": "Low",
        "level": 3,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 2,
    },
    {
        "name": "Trivial",
        "level": 4,
        "fg_color": "#ffffff",
        "bg_color": "#ffffff",
        "organization_id": 2,
    },
]

status = [
    {
        "name": "Open",
        "bg_color": "#ffffff",
        "fg_color": "#ffffff",
        "organization_id": 1,
        "status_category": "OPEN",
    },
    {
        "name": "Pending",
        "bg_color": "#ffffff",
        "fg_color": "#ffffff",
        "organization_id": 1,
        "is_default": True,
        "status_category": "PENDING",
    },
    {
        "name": "Closed",
        "bg_color": "#ffffff",
        "fg_color": "#ffffff",
        "organization_id": 1,
        "status_category": "CLOSED",
    },
]
status2 = [
    {
        "name": "In-Progress",
        "bg_color": "#ffffff",
        "fg_color": "#ffffff",
        "organization_id": 2,
        "status_category": "OPEN",
    },
    {
        "name": "Pending",
        "bg_color": "#ffffff",
        "fg_color": "#ffffff",
        "organization_id": 2,
        "is_default": True,
        "status_category": "PENDING",
    },
    {
        "name": "Closed",
        "color": "#ffffff",
        "organization_id": 2,
        "bg_color": "#ffffff",
        "fg_color": "#ffffff",
        "status_category": "CLOSED",
    },
]

async def priority_seed():
    for i in priorities:
        record = await TicketPriority.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await TicketPriority.create(
                name=i["name"],
                level=i["level"],
                bg_color=i["bg_color"],
                fg_color=i["fg_color"],
                organization_id=i["organization_id"],
            )
            print("TicketPriority 1 created")
        else:
            print("TicketPriority 1 already created")

    for i in priorities2:
        record = await TicketPriority.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await TicketPriority.create(
                name=i["name"],
                level=i["level"],
                bg_color=i["bg_color"],
                fg_color=i["fg_color"],
                organization_id=i["organization_id"],
            )
            print("TicketPriority2 created")
        else:
            print("TicketPriority2 already created")


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
                bg_color=i["bg_color"],
                fg_color=i["fg_color"],
                organization_id=i["organization_id"],
                is_default=bool(i.get("is_default", False)),
                status_category=i["status_category"],
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
                bg_color=i["bg_color"],
                fg_color=i["fg_color"],
                organization_id=i["organization_id"],
                is_default=bool(i.get("is_default", False)),
                status_category=i["status_category"],
            )
            print("Status 2 created")
        else:
            print("Status 2 already created")


async def sla_seed_dummy():
    record = await TicketSLA.find_one(
        where={
            "name": {"mode": "insensitive", "value": "test_sla"},
        }
    )
    record2 = await TicketSLA.find_one(
        where={
            "name": {"mode": "insensitive", "value": "test_sla2"},
        }
    )
    if not record:
        await TicketSLA.create(
            name="test_sla",
            response_time=18000,  # 5 hours
            resolution_time=432000,  # 5 days
            organization_id=1,
            issued_by=1,
            is_default=True,
        )
        print("Test TicketSLA 1 has been created")
    else:
        print("Test TicketSLA 1 already exists")

    if not record2:
        await TicketSLA.create(
            name="test_sla2",
            response_time=18000,  # 5 hours
            resolution_time=432000,  # 5 days
            organization_id=2,
            issued_by=2,
            is_default=True,
        )
        print("Test TicketSLA 2 has been created")
    else:
        print("Test TicketSLA 2 already exists")
