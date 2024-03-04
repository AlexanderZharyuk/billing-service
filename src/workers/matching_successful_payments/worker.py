from datetime import timedelta

from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.interfaces import TypeProvider
from src.v1.payments.models import Payment, PaymentCreate, PaymentMetadata, PaymentStatusEnum
from src.workers.interfaces import BasePaymentMatchingWorker
from src.workers.matching_successful_payments import logger


class MatchingSuccessPayments(BasePaymentMatchingWorker):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA):
        super().__init__(session, type_provider)
        self.payment_status = PaymentStatusEnum.SUCCEEDED.value
        self.early_date = self.date_now - timedelta(hours=1)

    async def matching_data(self) -> None:
        params = {
            "status": self.payment_status,
            "created_at.gt": self.early_date.strftime(self.date_format),
            "created_at.lt": self.date_now.strftime(self.date_format),
        }
        filter_ = (
            Payment.status == self.payment_status,
            Payment.created_at > self.early_date,
            Payment.created_at < self.date_now,
        )
        payments_for_provider = await super().get_payments_for_provider(params=params)
        payments_for_db = await super().get_payments_for_db(filter_=filter_)
        different_items = set(payments_for_provider).difference(set(payments_for_db))
        if not different_items == 0:
            logger.info("No discrepancies in payments were found.")
            return
        for item in different_items:
            object_ = await self.provider.get(type_object=self.type_object, entity_id=item)
            payment_metadata = PaymentMetadata(**object_.metadata)
            payment = PaymentCreate(
                payment_provider_id=payment_metadata.payment_provider_id,
                payment_method=object_.payment_method.type,
                status=self.payment_status,
                currency=object_.amount.currency,
                amount=object_.amount.value,
                external_payment_id=object_.id,
            )
            create_payment = await super().create(payment)
            logger.info(f"A payment has been created with id {create_payment.id}.")
            subscription_create = await super().create_subscription(
                metadata=payment_metadata, payment=create_payment
            )
            logger.info(f"A subscription has been created with id {subscription_create.id}.")
