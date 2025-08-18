from datetime import datetime
from typing import Any, List

from src.common.utils import hash_password
from src.models import User

user_data = [
    {
        "email": "test@gmail.com",
        "password": "test12345",
        "name": "test",
        "organization_id": 1,
    },
    {
        "email": "test2@gmail.com",
        "password": "test12345",
        "name": "test",
        "organization_id": 2,
    },
    {"email": "test3@gmail.com", "password": "test12345", "name": "test"},
    {"email": "test4@gmail.com", "password": "test12345", "name": "test"},
    {"email": "test5@gmail.com", "password": "test12345", "name": "test"},
    {"email": "test6@gmail.com", "password": "test12345", "name": "test"},
]


async def user_seed_dummy():
    # checking if test user exists or not
    for user in user_data:

        user_exist = await User.find_one(where={"email": user["email"]})

        if not user_exist:

            usr = await User.create(
                email=user["email"],
                name=user["name"],
                password=hash_password(user["password"]),
            )
            payload = {"id": usr.id, "email_verified_at": datetime.utcnow()}
            if "organization_id" in user:
                payload["attributes"] = {"organization_id": user["organization_id"]}
            await User.update(**payload)
            print(f"The user {user['email']} created")
