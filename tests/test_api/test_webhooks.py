import json
import os

import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

webhook_url = "api/v1/webhooks/"


async def test_webhook_yookassa(http_client: AsyncClient):
    body = {}
    response = await http_client.post(webhook_url + "yookassa", json=body)
    received = response.json()["received"]
    assert response.status_code == status.HTTP_200_OK
    assert received is True
