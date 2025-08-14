from src.models import TicketPriority, TicketSLA, TicketStatus

priorities = [
    {
        "name": "critical",
        "level": 0,
        "bg_color": "#FAD6D5",
        "fg_color": "#F61818",
        "organization_id": 1,
    },
    {
        "name": "high",
        "level": 1,
        "bg_color": "#FFF0D2",
        "fg_color": "#F5CE31",
        "organization_id": 1,
    },
    {
        "name": "medium",
        "level": 2,
        "bg_color": "#DAE8FA",
        "fg_color": "#3872B7",
        "organization_id": 1,
    },
    {
        "name": "low",
        "level": 3,
        "bg_color": "#E5F9DB",
        "fg_color": "#009959",
        "organization_id": 1,
    },
]
priorities2 = [
    {
        "name": "critical",
        "level": 0,
        "bg_color": "#FAD6D5",
        "fg_color": "#F61818",
        "organization_id": 2,
    },
    {
        "name": "high",
        "level": 1,
        "bg_color": "#FFF0D2",
        "fg_color": "#F5CE31",
        "organization_id": 2,
    },
    {
        "name": "medium",
        "level": 2,
        "bg_color": "#DAE8FA",
        "fg_color": "#3872B7",
        "organization_id": 2,
    },
    {
        "name": "low",
        "level": 3,
        "bg_color": "#E5F9DB",
        "fg_color": "#009959",
        "organization_id": 2,
    },
]

status = [
    {
        "name": "Unassigned",
        "bg_color": "#F61818",
        "fg_color": "#ffffff",
        "organization_id": 1,
        "status_category": "pending",
    },
    {
        "name": "Assigned",
        "bg_color": "#FFF0D2",
        "fg_color": "#ffffff",
        "organization_id": 1,
        "status_category": "open",
    },
    {
        "name": "Solved",
        "bg_color": "#009959",
        "fg_color": "#ffffff",
        "organization_id": 1,
        "status_category": "closed",
    },
    {
        "name": "Reopened",
        "bg_color": "#DAE8FA",
        "fg_color": "#ffffff",
        "organization_id": 1,
        "status_category": "reopened",
    },
]
status2 = [
    {
        "name": "Unassigned",
        "bg_color": "#F61818",
        "fg_color": "#ffffff",
        "organization_id": 2,
        "status_category": "pending",
    },
    {
        "name": "Assigned",
        "bg_color": "#FFF0D2",
        "fg_color": "#ffffff",
        "organization_id": 2,
        "status_category": "open",
    },
    {
        "name": "Solved",
        "bg_color": "#009959",
        "fg_color": "#ffffff",
        "organization_id": 2,
        "status_category": "closed",
    },
    {
        "name": "Reopened",
        "bg_color": "#DAE8FA",
        "fg_color": "#ffffff",
        "organization_id": 2,
        "status_category": "reopened",
    },
]
default_ticket_sla = [
    {
        "name": "Critical Standard",
        "response_time": 300,  # 4 hours in seconds
        "resolution_time": 600,  # 24 hours in seconds
        "organization_id": 1,
        "priority_id": 1,
    },
    {
        "name": "High Standard",
        "response_time": 18400,
        "resolution_time": 106400,
        "organization_id": 1,
        "priority_id": 2,
    },
    {
        "name": "Medium Standard",
        "response_time": 22400,
        "resolution_time": 146400,
        "organization_id": 1,
        "priority_id": 3,
    },
    {
        "name": "Low Standard",
        "response_time": 22400,
        "resolution_time": 146400,
        "organization_id": 1,
        "priority_id": 4,
    },
]
default_ticket_sla2 = [
    {
        "name": "Critical Standard",
        "response_time": 300,  # 4 hours in seconds
        "resolution_time": 600,  # 24 hours in seconds
        "organization_id": 2,
        "priority_id": 1,
    },
    {
        "name": "High Standard",
        "response_time": 18400,
        "resolution_time": 106400,
        "organization_id": 2,
        "priority_id": 2,
    },
    {
        "name": "Medium Standard",
        "response_time": 22400,
        "resolution_time": 146400,
        "organization_id": 2,
        "priority_id": 3,
    },
    {
        "name": "Low Standard",
        "response_time": 22400,
        "resolution_time": 146400,
        "organization_id": 2,
        "priority_id": 4,
    },
]


async def priority_seed():
    for i in priorities:
        record = await TicketPriority.find_one_without_tenant(
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
        record2 = await TicketPriority.find_one(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record2:
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


async def ticket_status_seed():
    for i in status:
        record = await TicketStatus.find_one_without_tenant(
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
        record = await TicketStatus.find_one_without_tenant(
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
    for i in default_ticket_sla:
        record = await TicketSLA.find_one_without_tenant(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await TicketSLA.create(
                name=i["name"],
                response_time=i["response_time"],
                resolution_time=i["resolution_time"],
                organization_id=i["organization_id"],
                priority_id=i["priority_id"],
            )
            print("Test TicketSLA 1 has been created")
        else:
            print("Test TicketSLA 1 already exists")
    for i in default_ticket_sla2:
        record = await TicketSLA.find_one_without_tenant(
            where={
                "name": {"mode": "insensitive", "value": i["name"]},
                "organization_id": i["organization_id"],
            }
        )
        if not record:
            await TicketSLA.create(
                name=i["name"],
                response_time=i["response_time"],
                resolution_time=i["resolution_time"],
                organization_id=i["organization_id"],
                priority_id=i["priority_id"],
            )
            print("Test TicketSLA 2 has been created")
        else:
            print("Test TicketSLA 2 already exists")
