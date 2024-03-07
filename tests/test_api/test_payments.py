import pytest
from starlette import status
from httpx import AsyncClient
import json

pytestmark = pytest.mark.asyncio

admin_payments_url = "/api/v1/admin/payments/"
payments_url = "/api/v1/payments/"


async def test_get_payment(http_client: AsyncClient):
    response = await http_client.get(payments_url, params={"payment_id": 1})
    assert response.status_code == status.HTTP_200_OK


async def test_get_payments(http_client: AsyncClient):
    response = await http_client.get(payments_url)
    data = len(response.json()["data"])
    assert response.status_code == status.HTTP_200_OK


async def test_update_plan(http_client):
    response = await http_client.request(
        "PUT",
        admin_payments_url + "{id}",
        params={"payment_id": 2},
        headers={"Content-Type": "application/json"},
        data=json.dumps({"name": "Archive Plan"}),
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_plan(http_client):
    response = await http_client.request(
        "DELETE",
        admin_payments_url + "{id}",
        params={"payment_id": 3},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
#
