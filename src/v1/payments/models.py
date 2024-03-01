from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint
from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin
from src.v1.payment_providers.models import PaymentProvider
from src.v1.plans import Plan

if TYPE_CHECKING:
    from src.v1.subscriptions.models import Subscription
    from src.v1.payment_providers.models import PaymentProvider


class PaymentStatusEnum(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    EXPIRED = "expired"
    CANCELED = "cancelled"


class CurrencyEnum(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class PaymentMethodsEnum(str, Enum):
    BANK_CARD = "bank_card"
    YOO_MONEY = "yoo_money"
    SBERBANK = "sberbank"
    TINKOFF_BANK = "tinkoff_bank"
    SBP = "sbp"


class Payment(Base, TimeStampedMixin, table=True):
    """Модель таблицы с платежами."""

    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive_integer"),)

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    subscription: "Subscription" = Relationship(back_populates="payments")
    payment_provider_id: int = Field(foreign_key="payment_providers.id")
    payment_provider: "PaymentProvider" = Relationship(back_populates="payments")
    payment_type: PaymentStatusEnum = Field(
        default=PaymentMethodsEnum.BANK_CARD,
    )
    status: PaymentStatusEnum = Field(
        default=PaymentStatusEnum.CREATED,
    )
    currency: CurrencyEnum = Field(
        default=CurrencyEnum.RUB,
    )
    amount: Decimal = Field(max_digits=8, decimal_places=2)
    external_payment_id: Optional[str] = Field(default=None, max_length=50)
    external_payment_type_id: Optional[str] = Field(default=None, max_length=50)

    def __repr__(self) -> str:
        return f"Payment(id={self.id!r}, status={self.status!r}, amount={self.amount!r}, currency={self.currency!r})"


class PaymentCreate(SQLModel):
    plan: Plan
    payment_provider_id: int
    payment_method: PaymentMethodsEnum
    currency: CurrencyEnum
    amount: Decimal


class PaymentUpdate(SQLModel):
    status: Optional[PaymentStatusEnum] = Field(default=None)
    external_payment_id: Optional[str] = Field(default=None)
    external_payment_type_id: Optional[str] = Field(default=None)


class PaymentMetadata(SQLModel):
    subscription_id: int
    payment_provider_id: int
    user_id: UUID
    plan_id: int


class SinglePaymentResponse(BaseResponseBody):
    data: Payment


class SeveralPaymentsResponse(BaseResponseBody):
    data: list[Payment] | dict
