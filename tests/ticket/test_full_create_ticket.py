import pytest
from httpx import AsyncClient

demo_data = {
    "title": "Test",
    "description": "Test descriptin",
    "sla_id": 4,
    "contact": {
        "first_name": "test",
        "last_name": "test",
        "email": "test3@gmail.com",
        "phone": "+977 9800000000",
    },
}


@pytest.mark.asyncio
async def test_full_create_ticket():
    async with AsyncClient() as ac:
        login_response = await ac.post(
            "http://localhost:8000/auth/login",
            json={"email": "test@gmail.com", "password": "testpass"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            "http://localhost:8000/tickets/full-create", json=demo_data, headers=headers
        )

    assert response.status_code == 201
