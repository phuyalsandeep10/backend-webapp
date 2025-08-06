from typing import List

import pytest
from httpx import AsyncClient

from ..common import get_login_token


@pytest.mark.asyncio
async def test_list_priorities():
    """
    Test to list all the priorities
    """
    access_token = get_login_token()

    async with AsyncClient(follow_redirects=True) as ac:
        response = await ac.get(
            "http://localhost:8000/tickets/priority",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert ("success" in data) and data["success"] is True
    assert ("message" in data) and data["message"] == "Successfully listed priorities"
    assert ("data" in data) and isinstance(data["data"], List)


@pytest.mark.asyncio
async def test_get_priority_by_id():
    """
    Test to list particular priority by id
    """
    access_token = get_login_token()

    async with AsyncClient(follow_redirects=True) as ac:
        response = await ac.get(
            "http://localhost:8000/tickets/priority/2",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert ("success" in data) and data["success"] is True
    assert ("message" in data) and data["message"] == "Successfully listed priority"
    assert ("data" in data) and isinstance(data["data"], dict)
