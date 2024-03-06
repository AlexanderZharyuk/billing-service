from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.v1.payments.models import Payment, PaymentStatusEnum, PaymentUpdate
from src.v1.payment_providers.service import TypeProvider
from src.workers.interfaces import BasePaymentMatchingWorker
from src.workers.matching_expire_payments import logger


class MatchingExpirePayments(BasePaymentMatchingWorker):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA.value):
        super().__init__(session, type_provider)
        self.payment_waiting_date = settings.payment_waiting_date

    async def matching_data(self) -> None:
        filter_ = (
            Payment.status == PaymentStatusEnum.PENDING.value,
            Payment.created_at < self.date_now,
        )
        await self.fix_expired_payments(filter_=filter_)

    async def fix_expired_payments(self, filter_: tuple) -> None:
        payments_for_db = await super().get_payments_for_db(filter_=filter_)
        if not payments_for_db:
            logger.info(f"Payments older than {self.payment_waiting_date} days with the status 'PENDING' have not been detected.")
            return
        for item in payments_for_db:
            payment = await super().get_one_by_filter((Payment.external_payment_id == item,))
            delta_days = (self.date_now - payment.created_at).days
            if delta_days >= self.payment_waiting_date:
                payment_update = await super().update_payment(
                    entity_id=payment.id, data=PaymentUpdate(status=PaymentStatusEnum.EXPIRED)
                )
                logger.info(
                    f"The payment status with id {payment_update.id} has been updated to 'EXPIRED'."
                )
