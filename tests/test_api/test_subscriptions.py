import pytest
import pytest
import os
from starlette import status
import json

pytestmark = pytest.mark.anyio

base_url = os.getenv("BILLING_URL", "http://localhost:8000/api/v1")
admin_subscription_url = base_url + "/admin/subscriptions/"
subscription_url = base_url + "/subscriptions/"


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_subscription(http_client):
    pass


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_subscriptions(http_client):
    pass


async def test_create_subscription(http_client):
    response = await http_client.request(
        "POST",
        admin_subscription_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"plan_id": 999999, "payment_provider_id": 1, "currency": "RUB"}),
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_pause_subscription(http_client):
    response = await http_client.request(
        "PATCH",
        admin_subscription_url + "{id}",
        headers={"Content-Type": "application/json"},
        params={"subscription_id": 999999},
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_subscription(http_client):
    response = await http_client.request(
        "DELETE",
        admin_subscription_url + "{id}",
        params={"subscription_id": 999999},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
