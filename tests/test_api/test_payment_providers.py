import json

import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

payment_providers_admin_url = "/api/v1/admin/payment_providers/"
payment_providers_url = "/api/v1/payments/"


async def test_get_payment_provider(http_client: AsyncClient):
    response = await http_client.get(payment_providers_url, params={"payment_id": 1})
    assert response.status_code == status.HTTP_200_OK


async def test_get_payment_providers(http_client: AsyncClient):
    response = await http_client.get(payment_providers_url)
    assert response.status_code == status.HTTP_200_OK


async def test_create_payment_providers(http_client: AsyncClient):
    provider = {"name": "Tinkoff", "description": None, "is_active": True}
    response = await http_client.post(payment_providers_admin_url, json=provider)
    assert response.status_code == status.HTTP_201_CREATED
