import pytest
import os
from starlette import status
import json

pytestmark = pytest.mark.anyio

base_url = os.getenv("BILLING_URL", "http://localhost:8000/api/v1")
plans_url = base_url + "/plans/"


async def test_get_plan_bad(http_client):
    expected_data = {"detail": {"code": 1001, "message": "Plan not found"}}
    response = await http_client.request(
        "GET",
        plans_url + "{id}",
        params={"plan_id": 222}
    )
    print(response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_data


async def test_create_plan(http_client):
    response = await http_client.request(
        "POST",
        plans_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
              "name": "Test Plan",
              "description": "string",
              "is_active": True,
              "is_recurring": True,
              "duration": 0,
              "duration_unit": "string"
            })
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_plan(http_client):
    response = await http_client.request(
        "PUT",
        plans_url + "{id}",
        params={"plan_id": 3},
        headers={"Content-Type": "application/json"},
        data=json.dumps({"name": "New Plan"})
    )
    assert response.status_code == status.HTTP_200_OK


async def test_get_plan_ok(http_client):
    expected_data = "New Plan"

    response = await http_client.request(
        "GET",
        plans_url + "{id}",
        params={"plan_id": 3}
    )
    print(response)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["name"] == expected_data


async def test_get_plans(http_client):
    response = await http_client.request(
        "GET",
        plans_url,
    )
    print(response)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) > 0


async def test_delete_plan(http_client):
    response = await http_client.request(
        "DELETE",
        plans_url + "{id}",
        params={"plan_id": 123}
    )
    print(response)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
