import pytest
from src.workers.expire_subscriptions.worker import ExpireSubscriptionsWorker
from httpx import AsyncClient
from src.v1.plans import Plan
from tests.utils.testing_data import test_data
from datetime import datetime

pytestmark = pytest.mark.asyncio


async def test_get_subscriptions(expire_subscriptions_worker: ExpireSubscriptionsWorker):
    expected_cnt = 2
    subscriptions = await expire_subscriptions_worker.get_subscriptions()
    assert len(subscriptions) == expected_cnt


async def test_change_to_expired(http_client: AsyncClient, expire_subscriptions_worker: ExpireSubscriptionsWorker):
    url = "api/v1/admin/subscriptions/1"
    response = await http_client.get(url)
    assert response.json()["data"]["status"] == "active"
    await expire_subscriptions_worker.main()
    response = await http_client.get(url)
    assert response.json()["data"]["status"] == "expired"
