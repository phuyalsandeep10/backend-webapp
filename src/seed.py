import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import src.models
from src.common.utils import hash_password
from src.modules.auth.models import User
from src.modules.organizations.models import Organization


async def test_user_seed():
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
    print("Test User already exists")


async def test_organization():

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


async def priority_seed():
    pass


async def seed_func():
    await test_organization()
    # await test_user_seed()


if __name__ == "__main__":
    asyncio.run(seed_func())
