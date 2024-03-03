import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession

from src.workers.autopayment_worker import logger
from src.workers.autopayment_worker.worker import AutopaymentsWorker
from src.workers.helpers import session_injection


@session_injection
async def main(session: AsyncSession = None):
    logger.info("Autopayment worker launched.")
    logger.info("The worker's work cycle has been started.")
    worker = AutopaymentsWorker(session=session)
    await worker.autopayments()
    logger.info("The worker has completed the work.")


if __name__ == "__main__":
    asyncio.run(main())
