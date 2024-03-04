import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession

from src.workers.expire_subscriptions_worker import logger
from src.workers.expire_subscriptions_worker.worker import ExpireSubscriptionsWorker
from src.workers.helpers import session_injection


@session_injection
async def main(session: AsyncSession = None):
    logger.info("Expire subscriptions worker launched.")
    logger.info("The worker's work cycle has been started.")
    worker = ExpireSubscriptionsWorker(session=session)
    await worker.main()
    logger.info("The worker has completed the work.")


if __name__ == "__main__":
    asyncio.run(main())
