from src.modules.organizations.models import OrganizationMember

organization_members = [
    {
        "user_id": 3,
        "organization_id": 1,
    },
    {
        "user_id": 4,
        "organization_id": 1,
    },
    {
        "user_id": 5,
        "organization_id": 2,
    },
    {
        "user_id": 6,
        "organization_id": 2,
    },
]


async def organizaiton_members_seed_dummy():
    # checking if test user exists or not
    for user in organization_members:
        user_exist = await OrganizationMember.find_one(
            where={"user_id": user["user_id"]}
        )

        if not user_exist:
            usr = await OrganizationMember.create(**user)
            print("Organization member created")
