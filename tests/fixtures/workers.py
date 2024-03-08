import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.workers.autopayments.worker import AutopaymentsWorker
from src.workers.expire_subscriptions.worker import ExpireSubscriptionsWorker
from src.workers.matching_expire_payments.worker import MatchingExpirePayments
from src.workers.matching_pending_payments.worker import MatchingPendingPayments
from src.workers.matching_successful_payments.worker import MatchingSuccessPayments


@pytest.fixture(scope="session")
async def autopayment_worker(http_client: AsyncSession):
    worker = AutopaymentsWorker(http_client)
    return worker


@pytest.fixture(scope="session")
async def expire_subscriptions_worker(http_client: AsyncSession):
    worker = ExpireSubscriptionsWorker(http_client)
    return worker


@pytest.fixture(scope="session")
async def matching_expire_payments_worker(https_client: AsyncSession):
    worker = MatchingExpirePayments(https_client)
    return worker


@pytest.fixture(scope="session")
async def matching_pending_payments(http_client: AsyncSession):
    worker = MatchingPendingPayments(http_client)
    return worker


@pytest.fixture(scope="session")
async def matching_successful_payments(http_client: AsyncSession):
    worker = MatchingSuccessPayments(http_client)
    return worker



