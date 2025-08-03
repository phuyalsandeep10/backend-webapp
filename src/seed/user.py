
from src.models import User
from src.common.utils import hash_password
from datetime import datetime

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