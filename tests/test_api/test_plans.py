import pytest
from starlette import status
from httpx import AsyncClient


pytestmark = pytest.mark.anyio

admin_plans_url = "/api/v1/admin/plans/"
plans_url = "/api/v1/plans/"


async def test_get_plan(http_client: AsyncClient):
    expected_data = "First Plan"
    response = await http_client.get(plans_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["name"] == expected_data


# # TODO нужна фикстура, добавляющая строку в таблицу
# async def test_get_plans(http_client):
#     response = await http_client.request(
#         "GET",
#         plans_url,
#     )
#     print(response)
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.json()["data"]) > 0
#

# async def test_create_plan(api_session):
#     response = await api_session.post(
#         admin_plans_url,
#         headers={"Content-Type": "application/json"},
#         data=json.dumps(
#             {
#                 "name": "Test Plan",
#                 "description": "string",
#                 "is_active": True,
#                 "is_recurring": True,
#                 "duration": 0,
#                 "duration_unit": "string",
#             }
#         ),
#     )
#     assert response.status_code == status.HTTP_201_CREATED

#
# async def test_update_plan(http_client):
#     response = await http_client.request(
#         "PUT",
#         admin_plans_url + "{id}",
#         params={"plan_id": 100001},
#         headers={"Content-Type": "application/json"},
#         data=json.dumps({"name": "New Test Plan"}),
#     )
#     assert response.status_code == status.HTTP_200_OK
#
#
# async def test_delete_plan(http_client):
#     response = await http_client.request(
#         "DELETE",
#         admin_plans_url + "{id}",
#         params={"plan_id": 100001},
#     )
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json()["data"]["success"] is True
