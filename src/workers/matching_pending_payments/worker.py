from datetime import timedelta

from sqlmodel.ext.asyncio.session import AsyncSession

from src.v1.payments.models import Payment, PaymentMetadata, PaymentStatusEnum, PaymentUpdate
from src.v1.payment_providers.service import TypeProvider
from src.workers.interfaces import BasePaymentMatchingWorker
from src.workers.matching_pending_payments import logger


class MatchingPendingPayments(BasePaymentMatchingWorker):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA.value):
        super().__init__(session, type_provider)
        self.early_date = self.date_now - timedelta(hours=1)

    async def matching_data(self) -> None:
        params = {
            "status": PaymentStatusEnum.SUCCEEDED.value,
            "created_at.gt": self.early_date.strftime(self.date_format),
            "created_at.lt": self.date_now.strftime(self.date_format),
        }
        filter_ = (
            Payment.status == PaymentStatusEnum.PENDING.value,
            Payment.created_at > self.early_date,
            Payment.created_at < self.date_now,
        )
        await self.fix_paid_payments(params=params, filter_=filter_)

    async def fix_paid_payments(self, params: dict, filter_: tuple) -> None:
        payments_for_provider = await super().get_payments_for_provider(params=params)
        payments_for_db = await super().get_payments_for_db(filter_=filter_)
        intersection_items = set(payments_for_db).intersection(set(payments_for_provider))
        if not intersection_items:
            logger.info("No fixed paid payments were found.")
            return
        for item in intersection_items:
            object_ = await self.provider.get(type_object=self.type_object, entity_id=item)
            payment = await super().get_one_by_filter((Payment.external_payment_id == item,))
            payment_metadata = PaymentMetadata(**object_.metadata)
            subscription_create = await super().create_subscription(
                metadata=payment_metadata, commit=False
            )
            await self.session.flush()
            payment_update = await super().update_payment(
                entity_id=payment.id, data=PaymentUpdate(status=PaymentStatusEnum.SUCCEEDED, subscription_id=subscription_create.id), commit=False
            )
            await super().session_commit()
            logger.info(
                f"The payment status with id {payment_update.id} has been updated to 'SUCCEEDED'."
            )
            logger.info(f"A subscription has been created with id {subscription_create.id}.")
