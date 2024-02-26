from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship, CheckConstraint

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin


class PaymentStatusEnum(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
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
    invoice_id: int = Field(foreign_key="invoices.id")
    invoice: "Invoice" = Relationship(back_populates="payments")
    payment_provider_id: int = Field(foreign_key="payment_providers.id")
    payment_provider: "PaymentProvider" = Relationship(back_populates="payments")
    status: PaymentStatusEnum = Field(
        default=PaymentStatusEnum.CREATED,
    )
    currency: CurrencyEnum = Field(
        default=CurrencyEnum.RUB,
    )
    amount: int

    def __repr__(self) -> str:
        return f"Payment(id={self.id!r}, name={self.name!r})"


class PaymentCreate(SQLModel):
    name: str
    invoice_id: int
    payment_provider_id: int
    status: PaymentStatusEnum
    currency: CurrencyEnum
    amount: int


class PaymentUpdate(PaymentCreate):
    ...


class SinglePaymentResponse(BaseResponseBody):
    data: Payment


class SeveralPaymentsResponse(BaseResponseBody):
    data: list[Payment] | dict
