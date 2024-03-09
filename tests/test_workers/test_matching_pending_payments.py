import pytest
from httpx import AsyncClient

from src.workers.matching_pending_payments.worker import \
    MatchingPendingPayments

pytestmark = pytest.mark.asyncio


async def test_matching_data(
    http_client: AsyncClient, matching_pending_payments_worker: MatchingPendingPayments
):
    url = "/api/v1/payments/1"
    response = await http_client.get(url)
    assert response.json()["data"]["status"] == "pending"
    await matching_pending_payments_worker.matching_data()
    response = await http_client.get(url)
    assert response.json()["data"]["status"] == "succeeded"
