import pytest
from httpx import AsyncClient

from src.workers.matching_expire_payments.worker import MatchingExpirePayments

pytestmark = pytest.mark.asyncio


async def test_matching_data(
    http_client: AsyncClient, matching_expire_payments_worker: MatchingExpirePayments
):
    url = "/api/v1/payments/1"
    response = await http_client.get(url)
    assert response.json()["data"]["status"] == "pending"
    await matching_expire_payments_worker.matching_data()
    response = await http_client.get(url)
    assert response.json()["data"]["status"] == "expired"
