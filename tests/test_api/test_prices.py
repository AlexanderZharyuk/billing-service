import pytest
from starlette import status
from httpx import AsyncClient
import json

pytestmark = pytest.mark.asyncio

admin_price_url = "api/v1/admin/prices/"
price_url = "api/v1/prices/"


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_price():
    pass


async def test_get_prices(http_client: AsyncClient):
    expected_cnt = 3
    response = await http_client.get(price_url)
    assert response.status_code == status.HTTP_200_OK
    cnt = len(response.json()["data"])
    assert expected_cnt == cnt


async def test_create_price(http_client: AsyncClient):
    body = {"plan_id": 3, "currency": "RUB", "amount": 300}
    response = await http_client.post(
        admin_price_url,
        json=body
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_price(http_client: AsyncClient):
    price_id = 2
    body = {"currency": "RUB", "amount": 150}
    response = await http_client.patch(
        admin_price_url + str(price_id),
        json=body
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_price(http_client: AsyncClient):
    price_id = 1
    response = await http_client.delete(admin_price_url + str(price_id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
