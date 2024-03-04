import pytest
import os
from starlette import status
import json

pytestmark = pytest.mark.anyio

base_url = os.getenv("BILLING_URL", "http://localhost:8000/api/v1")
admin_plans_url = base_url + "/admin/plans/"
plans_url = base_url + "/plans/"


# TODO нужна фикстура, добавляющая строку в таблицу
# async def test_get_plan(http_client):
#     expected_data = "New Plan"
#
#     response = await http_client.request(
#         "GET",
#         admin_plans_url + "{id}",
#         params={"plan_id": 999999}
#     )
#     print(response)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json()["data"]["name"] == expected_data


# TODO нужна фикстура, добавляющая строку в таблицу
# async def test_get_plans(http_client):
#     response = await http_client.request(
#         "GET",
#         plans_url,
#     )
#     print(response)
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.json()["data"]) > 0


async def test_create_plan(http_client):
    response = await http_client.request(
        "POST",
        admin_plans_url,
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
        admin_plans_url + "{id}",
        params={"plan_id": 999999},
        headers={"Content-Type": "application/json"},
        data=json.dumps({"name": "New Test Plan"})
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_plan(http_client):
    response = await http_client.request(
        "DELETE",
        admin_plans_url + "{id}",
        params={"plan_id": 999999},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True


