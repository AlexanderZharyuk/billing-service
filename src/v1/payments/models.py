from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint
from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLModelEnum

from src.models import BaseResponseBody, Base, TimeStampedMixin, CurrencyEnum
from src.v1.payment_providers.models import PaymentProvider

if TYPE_CHECKING:
    from src.v1.subscriptions.models import Subscription
    from src.v1.payment_providers.models import PaymentProvider


class PaymentStatusEnum(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    EXPIRED = "expired"
    CANCELED = "cancelled"
    REFUNDED = "refunded"


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

    class Config:
        arbitrary_types_allowed = True

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    subscription: "Subscription" = Relationship(back_populates="payments")
    payment_provider_id: int = Field(foreign_key="payment_providers.id")
    payment_provider: "PaymentProvider" = Relationship(back_populates="payments")
    payment_method: PaymentMethodsEnum = Field(
        default=PaymentMethodsEnum.BANK_CARD, sa_column=Column(SQLModelEnum(PaymentMethodsEnum))
    )
    status: PaymentStatusEnum = Field(
        default=PaymentStatusEnum.CREATED, sa_column=Column(SQLModelEnum(PaymentMethodsEnum))
    )
    currency: CurrencyEnum = Field(
        default=CurrencyEnum.RUB,
        sa_column=Column(SQLModelEnum(CurrencyEnum)),
    )
    amount: Decimal = Field(max_digits=8, decimal_places=2)
    external_payment_id: Optional[str] = Field(default=None, max_length=50)
    external_payment_type_id: Optional[str] = Field(default=None, max_length=50)

    def __repr__(self) -> str:
        return f"Payment(id={self.id!r}, status={self.status!r}, amount={self.amount!r}, currency={self.currency!r})"


class PaymentCreate(SQLModel):
    plan_id: Optional[int] = Field(default=None)
    payment_provider_id: int
    payment_method: PaymentMethodsEnum
    currency: CurrencyEnum
    amount: Decimal
    user_id: Optional[UUID] = Field(default=None)
    return_url: Optional[str] = Field(default=None)


class PaymentObjectCreate(SQLModel):
    payment_provider_id: int
    payment_method: PaymentStatusEnum
    status: PaymentMethodsEnum
    currency: CurrencyEnum
    amount: Decimal = Field(max_digits=8, decimal_places=2)
    external_payment_id: str
    external_payment_type_id: str


class PaymentUpdate(SQLModel):
    status: Optional[PaymentStatusEnum] = Field(default=None)
    external_payment_id: Optional[str] = Field(default=None)
    external_payment_type_id: Optional[str] = Field(default=None)


class PaymentMetadata(SQLModel):
    payment_provider_id: int
    user_id: str | UUID
    plan_id: int


class SinglePaymentResponse(BaseResponseBody):
    data: Payment


class SeveralPaymentsResponse(BaseResponseBody):
    data: list[Payment] | dict
