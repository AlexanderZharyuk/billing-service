import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.workers.autopayments.worker import AutopaymentsWorker
from src.workers.expire_subscriptions.worker import ExpireSubscriptionsWorker
from src.workers.matching_expire_payments.worker import MatchingExpirePayments
from src.workers.matching_pending_payments.worker import \
    MatchingPendingPayments
from src.workers.matching_successful_payments.worker import \
    MatchingSuccessPayments


@pytest_asyncio.fixture
async def autopayment_worker(db: AsyncSession):
    worker = AutopaymentsWorker(session=db)
    return worker


@pytest_asyncio.fixture
async def expire_subscriptions_worker(db: AsyncSession):
    worker = ExpireSubscriptionsWorker(session=db)
    return worker


@pytest_asyncio.fixture
async def matching_expire_payments_worker(db: AsyncSession):
    worker = MatchingExpirePayments(db)
    return worker


@pytest_asyncio.fixture
async def matching_pending_payments(db: AsyncSession):
    worker = MatchingPendingPayments(db)
    return worker


@pytest_asyncio.fixture
async def matching_successful_payments(db: AsyncSession):
    worker = MatchingSuccessPayments(db)
    return worker
