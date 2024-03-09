import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

admin_plans_url = "/api/v1/admin/plans/"
plans_url = "/api/v1/plans/"


async def test_get_plan(http_client: AsyncClient):
    plan_id = 1
    expected_data = "First Plan"
    response = await http_client.get(plans_url + str(plan_id))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]["name"]
    assert data == expected_data


async def test_get_user_plans(http_client: AsyncClient):
    expected_data = 2
    response = await http_client.get(plans_url)
    data = len(response.json()["data"])
    assert response.status_code == status.HTTP_200_OK
    assert data == expected_data


async def test_create_plan(http_client: AsyncClient):
    body = {
        "name": "Test Plan",
        "description": "string",
        "is_active": True,
        "is_recurring": True,
        "duration": 0,
        "duration_unit": "string",
    }
    response = await http_client.post(admin_plans_url, json=body)
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_plan(http_client: AsyncClient):
    plan_id = 2
    body = {"name": "Archive Plan"}
    response = await http_client.patch(
        admin_plans_url + str(plan_id),
        json=body,
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_plan(http_client: AsyncClient):
    plan_id = 3
    response = await http_client.delete(admin_plans_url + str(plan_id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
