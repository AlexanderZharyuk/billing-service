import uuid
from enum import Enum
from typing import Optional, List
from uuid import UUID

from sqlmodel import SQLModel, Field, Column, Relationship

from src.models import BaseResponseBody
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


class Payment(TimeStampedMixin, table=True):
    """Модель таблицы с платежами."""

    __tablename__ = "payments"

    id: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        schema_extra={"examples": [uuid.uuid4()]},
    )
    invoice_id: UUID = Field(foreign_key="invoices.id")
    invoice: "Invoice" = Relationship(back_populates="payment")
    payment_provider_id: UUID = Field(foreign_key="payment_providers.id")
    payment_provider: "PaymentProvider" = Relationship(back_populates="payment")
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
    description: Optional[str] = Field(default=None)
    available_entities: Optional[list] = Field(default=[])


class PaymentUpdate(PaymentCreate):
    ...


class SinglePaymentResponse(BaseResponseBody):
    data: Payment


class SeveralPaymentsResponse(BaseResponseBody):
    data: list[Payment] | dict
