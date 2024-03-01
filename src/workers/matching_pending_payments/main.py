import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.workers.helpers import session_injection
from src.workers.matching_pending_payments import logger
from src.workers.matching_pending_payments.worker import MatchingPendingPayments


@session_injection
async def main(session: AsyncSession = None):
    logger.info("Pending Payment Matching worker launched.")
    while True:
        logger.info("The worker's work cycle has been started.")
        worker = MatchingPendingPayments(session=session)
        await worker.matching_data()
        logger.info("The worker has completed the work.")
        break
        await asyncio.sleep(settings.worker_time_sleep) #ToDo: время сна должно быть дольше


if __name__ == "__main__":
    asyncio.run(main())
