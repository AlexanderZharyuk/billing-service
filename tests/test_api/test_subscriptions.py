import os

import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

admin_subscription_url = "api/v1/admin/subscriptions/"
subscription_url = "api/v1/subscriptions/"


async def test_get_user_subscription(http_client: AsyncClient):
    response = await http_client.get(subscription_url)
    assert response.status_code == status.HTTP_200_OK


async def test_get_subscription_pay_link(http_client: AsyncClient):
    response = await http_client.get(
        subscription_url + "get_pay_link",
        params={
            "plan_id": 1,
            "payment_provider_id": 1,
            "currency": "RUB",
            "user_id": "3f8cd1fb-0cc0-4e99-ba39-9478fa007731",
            "return_url": "yandex.ru",
        },
    )
    assert response.status_code == status.HTTP_200_OK


async def test_get_subscription_by_id(http_client: AsyncClient):
    subscription_id = 1
    response = await http_client.get(admin_subscription_url + str(subscription_id))
    assert response.status_code == status.HTTP_200_OK


async def test_pause_subscription(http_client: AsyncClient):
    body = {"status": "paused", "pause_duration_days": 7}
    subscription_id = 1
    response = await http_client.request(
        "PATCH",
        admin_subscription_url + str(subscription_id),
        json=body,
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_subscription(http_client: AsyncClient):
    subscription_id = 1
    response = await http_client.request(
        "DELETE",
        admin_subscription_url + str(subscription_id),
        params={"subscription_id": 1},
    )
    assert response.status_code == status.HTTP_200_OK
