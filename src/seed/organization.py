from src.config.settings import settings
from src.models import Organization, OrganizationMember, TicketPriority, User


async def organization_seed_dummy():

    user = await User.find_one(where={"email": "test@gmail.com"})
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
        await Organization.create(
            name="test",
            description="test description",
            slug="test".lower().replace(" ", "-"),  # Simple slug generation
            logo="test",
            owner_id=user.id,
            domain="https://test.com",
            identifier="test1",
            email_alias=f"jfajejcja@{settings.EMAIL_DOMAIN}",
        )

        print("Organization 1 created")
    else:
        print("Organization 1 already created")

    if not record2:
        await Organization.create(
            name="test2",
            description="test2 description",
            slug="test2".lower().replace(" ", "-"),  # Simple slug generation
            logo="test2",
            owner_id=user.id,
            domain="https://test2.com",
            identifier="test2",
            email_alias=f"qyrusenca@{settings.EMAIL_DOMAIN}",
        )

        print("Organization 2 created")
    else:
        print("Organization 2 already created")


async def organization_user_seed_dummy():
    user = await User.find_one(where={"email": "test@gmail.com"})
    org = await Organization.find_one(where={"name": "test"})
    if not user:
        await OrganizationMember.create(organization_id=org.id, user_id=user.id)

        print("User added to organization 1")
    else:
        print("User already added or there is not user with 1 id")
