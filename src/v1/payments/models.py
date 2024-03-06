from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint
from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLModelEnum

from src.models import BaseResponseBody, Base, TimeStampedMixin, CurrencyEnum

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
    subscription_id: int = Field(foreign_key="subscriptions.id", nullable=True)
    payment_provider_id: int = Field(foreign_key="payment_providers.id")
    payment_provider: "PaymentProvider" = Relationship(
        back_populates="payments", sa_relationship_kwargs={"lazy": "selectin"}
    )
    payment_method: PaymentMethodsEnum = Field(
        default=None, sa_column=Column(SQLModelEnum(PaymentMethodsEnum))
    )
    status: PaymentStatusEnum = Field(
        default=PaymentStatusEnum.CREATED, sa_column=Column(SQLModelEnum(PaymentStatusEnum))
    )
    currency: CurrencyEnum = Field(
        default=CurrencyEnum.RUB,
        sa_column=Column(SQLModelEnum(CurrencyEnum)),
    )
    amount: Decimal = Field(max_digits=8, decimal_places=2)
    external_payment_id: Optional[str] = Field(default=None, max_length=50, unique=True)

    def __repr__(self) -> str:
        return f"Payment(id ={self.id!r}, status={self.status!r}, amount={self.amount!r}, currency={self.currency!r})"


class PaymentCreate(SQLModel):
    payment_provider_id: int
    status: PaymentStatusEnum = Field(default=PaymentStatusEnum.CREATED)
    currency: CurrencyEnum
    amount: Decimal = Field(max_digits=8, decimal_places=2)
    external_payment_id: str = None
    external_payment_type_id: str = None


class PaymentUpdate(SQLModel):
    status: PaymentStatusEnum | None = Field(default=None)
    external_payment_id: str | None = Field(default=None)
    payment_method: str | None = Field(default=None)
    subscription_id: int | None = Field(default=None)


class PaymentMetadata(SQLModel):
    payment_provider_id: int
    user_id: int | UUID
    plan_id: int


class SinglePaymentResponse(BaseResponseBody):
    data: Payment


class SeveralPaymentsResponse(BaseResponseBody):
    data: list[Payment] | dict
