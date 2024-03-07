import pytest
from starlette import status
from httpx import AsyncClient
import json

pytestmark = pytest.mark.asyncio

admin_plans_url = "/api/v1/admin/plans/"
plans_url = "/api/v1/plans/"


async def test_get_plan(http_client: AsyncClient):
    expected_data = "First Plan"
    response = await http_client.get(plans_url + "{id}", params={"plan_id": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]["name"]
    assert data == expected_data


async def test_get_user_plans(http_client: AsyncClient):
    expected_data = 2
    response = await http_client.get(plans_url)
    data = len(response.json()["data"])
    assert response.status_code == status.HTTP_200_OK
    assert data == expected_data


async def test_create_plan(http_client):
    response = await http_client.post(
        admin_plans_url,
        headers={"Content-Type": "application/json"},
        json={
                "name": "Test Plan",
                "description": "string",
                "is_active": True,
                "is_recurring": True,
                "duration": 0,
                "duration_unit": "string",
            }
        )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_plan(http_client):
    response = await http_client.request(
        "PUT",
        admin_plans_url + "{id}",
        params={"plan_id": 2},
        headers={"Content-Type": "application/json"},
        data=json.dumps({"name": "Archive Plan"}),
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_plan(http_client):
    response = await http_client.request(
        "DELETE",
        admin_plans_url + "{id}",
        params={"plan_id": 3},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
