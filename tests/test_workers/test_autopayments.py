import pytest
from src.workers.autopayments.worker import AutopaymentsWorker
from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.plans import Plan
from tests.utils.testing_data import test_data
from datetime import datetime

pytestmark = pytest.mark.asyncio


async def test_get_subscriptions(autopayment_worker: AutopaymentsWorker):
    expected_cnt = 2
    subscriptions = await autopayment_worker.get_subscriptions()
    assert len(subscriptions) == expected_cnt


async def test_calculating_end_date(autopayment_worker: AutopaymentsWorker):
    current_date = datetime.utcnow()
    plan = Plan(**test_data["plans"][0])
    end_date = await autopayment_worker.calculationg_end_date(plan)
    delta = end_date - current_date
    assert delta.days > 28


async def test_autopayments(http_client: AsyncSession, autopayment_worker: AutopaymentsWorker):
    ...
