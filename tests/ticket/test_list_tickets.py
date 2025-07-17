from typing import List

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tickets():
    async with AsyncClient(follow_redirects=True) as ac:
        response = await ac.get("http://localhost:8000/tickets")
    assert response.status_code == 200
    data = response.json()
    assert ("success" in data) and data["success"] is True
    assert ("message" in data) and data["message"] == "Successfully listed all tickets"
    assert ("data" in data) and isinstance(data["data"], List)
