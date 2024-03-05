from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.interfaces import TypeProvider
from src.v1.payments.models import Payment, PaymentStatusEnum
from src.workers.interfaces import BasePaymentMatchingWorker
from src.workers.matching_expire_payments import logger


class MatchingExpirePayments(BasePaymentMatchingWorker):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA):
        super().__init__(session, type_provider)
        self.payment_waiting_date = settings.payment_waiting_date

    async def matching_data(self) -> None:
        params = {
            "status": PaymentStatusEnum.SUCCEEDED.value,
            "created_at.lt": self.date_now.strftime(self.date_format),
        }
        filter_ = (
            Payment.status == PaymentStatusEnum.PENDING.value,
            Payment.created_at < self.date_now,
        )
        await self.fix_expired_payments(params=params, filter_=filter_)

    async def fix_expired_payments(self, params: dict, filter_: tuple) -> None:
        payments_for_provider = await super().get_payments_for_provider(params=params)
        payments_for_db = await super().get_payments_for_db(filter_=filter_)
        different_items = set(payments_for_db).difference(set(payments_for_provider))
        if not different_items:
            logger.info("There were no payments suspended in the 'PENDING' status.")
            return
        for item in different_items:
            payment = await super().get_one_by_filter((Payment.external_payment_id == item,))
            delta_days = (self.date_now - payment.created_at).days
            if delta_days >= self.payment_waiting_date:
                payment_update = await super().update_payment(
                    entity_id=payment.id, status=PaymentStatusEnum.EXPIRED
                )
                logger.info(
                    f"The payment status with id {payment_update.id} has been updated to 'EXPIRED'."
                )
