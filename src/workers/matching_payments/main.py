import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession

from src.workers.helpers import session_injection
from src.workers.matching_payments import logger
from src.workers.matching_payments.worker import MatchingSuccessPayments


@session_injection
async def main(session: AsyncSession = None):
    logger.info("Successful Payment Matching worker launched.")
    while True:
        logger.info("The worker's work cycle has been started.")
        worker = MatchingSuccessPayments(session=session)
        await worker.matching_data()
        logger.info("The worker has completed the work.")
        await asyncio.sleep(5)  # ToDo: add parametr "sleep" for config


if __name__ == "__main__":
    asyncio.run(main())