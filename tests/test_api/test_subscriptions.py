import pytest
import pytest
import os
from starlette import status
import json

pytestmark = pytest.mark.asyncio

admin_subscription_url = "api/v1/admin/subscriptions/"
subscription_url = "api/v1/subscriptions/"


async def test_get_subscription(http_client):
    response = await http_client.get(subscription_url)
    assert response.status_code == status.HTTP_200_OK


async def test_get_subscription_pay_link(http_client):
    response = await http_client.get(subscription_url + "get_pay_link",
                                     params={"plan_id": 1,
                                             "payment_provider_id": 1,
                                             "currency": "RUB",
                                             "user_id": "cc6e0b24-a46f-4c8e-beb0-b28479f3b203",
                                             "return_url": ""})
    assert response.status_code == status.HTTP_200_OK


async def test_pause_subscription(http_client):
    body = {"status": "paused", "pause_duration_days": 7}
    subscription_id = 1
    response = await http_client.request(
        "PATCH",
        admin_subscription_url+str(subscription_id),
        json=body,
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_subscription(http_client):
    subscription_id = 1
    response = await http_client.request(
        "DELETE",
        admin_subscription_url+str(subscription_id),
        params={"subscription_id": 1},
    )
    assert response.status_code == status.HTTP_200_OK
