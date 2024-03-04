import pytest
import os
from starlette import status
import json

pytestmark = pytest.mark.anyio

base_url = os.getenv("BILLING_URL", "http://localhost:8000/api/v1")
admin_price_url = base_url + "/admin/prices/"
price_url = base_url + "/prices/"


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_price():
    pass


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_prices():
    pass


async def test_create_price(http_client):
    response = await http_client.request(
        "POST",
        admin_price_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"plan_id": 999999, "currency": "RUB", "amount": 300})
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_price(http_client):
    response = await http_client.request(
        "PUT",
        admin_price_url + "{id}",
        headers={"Content-Type": "application/json"},
        params={"price_id": 999999},
        data=json.dumps({"currency": "RUB", "amount": 150})
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_price(http_client):
    response = await http_client.request(
        "DELETE",
        admin_price_url + "{id}",
        params={"price_id": 999999},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
