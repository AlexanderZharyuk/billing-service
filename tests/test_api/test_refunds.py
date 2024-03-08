import pytest
from starlette import status
from httpx import AsyncClient
import json

pytestmark = pytest.mark.asyncio

admin_refunds_url = "/api/v1/admin/refunds/"
refunds_url = "/api/v1/refunds/"


async def test_request_refund(http_client: AsyncClient):
    body = {"reason_id": 1, "subscription_id": 1, "user_id": "string", "additional_info": "string"}
    response = await http_client.post(refunds_url, json=body)
    assert response.status_code == status.HTTP_200_OK


async def test_create_refund_reason(http_client: AsyncClient):
    body = {"name": "I'm blind"}
    response = await http_client.post(admin_refunds_url + "reasons", json=body)
    assert response.status_code == status.HTTP_201_CREATED


async def test_make_refund(http_client: AsyncClient):
    body = {"payment_id": "1", "amount": 1, "currency": "RUB"}
    response = await http_client.post(admin_refunds_url, json=body)
    assert response.status_code == status.HTTP_201_CREATED
