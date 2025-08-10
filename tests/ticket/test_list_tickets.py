from typing import List

import pytest
from httpx import AsyncClient

from ..common import get_login_token


@pytest.mark.asyncio
async def test_list_tickets():
    access_token = get_login_token()
    async with AsyncClient(follow_redirects=True) as ac:
        response = await ac.get(
            "http://localhost:8000/tickets",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    assert response.status_code == 200
    data = response.json()
    assert ("success" in data) and data["success"] is True
    assert ("message" in data) and data["message"] == "Successfully listed all tickets"
    assert ("data" in data) and isinstance(data["data"], List)


@pytest.mark.asyncio
async def test_list_ticket_by_id():
    access_token = get_login_token()
    async with AsyncClient(follow_redirects=True) as ac:
        response = await ac.get(
            "http://localhost:8000/tickets/4",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    assert response.status_code == 200
    data = response.json()
    assert ("success" in data) and data["success"] is True
    assert ("message" in data) and data["message"] == "Successfully listed the ticket"
    assert ("data" in data) and isinstance(data["data"], List)
