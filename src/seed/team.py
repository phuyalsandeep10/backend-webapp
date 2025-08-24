from src.models import Organization, Team
from src.modules.team.models import TeamMember


async def department_team_seed_dummy():
    org = await Organization.find_one(where={"name": "test"})

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
            organization_id=org.id,
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


team_members = [
    {"team_id": 1, "user_id": 3},
    {
        "team_id": 1,
        "user_id": 4,
    },
    {
        "team_id": 2,
        "user_id": 5,
    },
    {
        "team_id": 2,
        "user_id": 6,
    },
]


async def team_members_seed_dummy():
    for team in team_members:
        team_exist = await TeamMember.find_one(
            where={"user_id": team["user_id"], "team_id": team["team_id"]}
        )
        if not team_exist:
            await TeamMember.create(**team)
            print("Team members created")
