from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship, CheckConstraint

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin
from src.v1.payment_providers.models import PaymentProvider


class PaymentStatusEnum(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    EXPIRED = "expired"
    CANCELED = "cancelled"


class CurrencyEnum(str, Enum):
    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class Payment(Base, TimeStampedMixin, table=True):
    """Модель таблицы с платежами."""

    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive_integer"),)

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    subscription_id: int = Field(foreign_key="subscriptions.id")
    subscription: "Subscription" = Relationship(back_populates="payments")
    payment_provider_id: int = Field(foreign_key="payment_providers.id")
    payment_provider: "PaymentProvider" = Relationship(back_populates="payments")
    actual_payment_id: str = Field(default=None, max_length=50)
    status: PaymentStatusEnum = Field(default=PaymentStatusEnum.CREATED,)
    currency: CurrencyEnum = Field(default=CurrencyEnum.RUB,)
    amount: Decimal = Field(max_digits=8, decimal_places=2)

    def __repr__(self) -> str:
        return f"Payment(id={self.id!r}, status={self.status!r}, amount={self.amount!r}, currency={self.currency!r})"


class PaymentCreate(SQLModel):
    name: str
    subscription_id: int
    payment_provider_id: int
    status: PaymentStatusEnum
    currency: CurrencyEnum
    amount: Decimal


class PaymentUpdate(SQLModel):
    name: Optional[str] = Field(default=None)
    status: Optional[PaymentStatusEnum] = Field(default=None)
    currency: Optional[CurrencyEnum] = Field(default=None)
    amount: Optional[Decimal] = Field(default=None)


class SinglePaymentResponse(BaseResponseBody):
    data: Payment


class SeveralPaymentsResponse(BaseResponseBody):
    data: list[Payment] | dict
