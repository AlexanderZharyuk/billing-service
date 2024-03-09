from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody, Base, CurrencyEnum
from src.models import TimeStampedMixin

if TYPE_CHECKING:
    from src.v1.payments.models import Payment


class PaymentProvider(Base, TimeStampedMixin, table=True):
    """Модель таблицы с платежными провайдерами."""

    __tablename__ = "payment_providers"

    id: int | None = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["payment_provider_X"]},
        nullable=False,
    )
    description: str | None = Field(
        default=None,
        schema_extra={"examples": ["payment_provider_X_description"]},
        nullable=True,
    )
    is_active: bool = Field(
        default=True,
        schema_extra={"examples": [True]},
        nullable=False,
    )
    payments: "Payment" = Relationship(back_populates="payment_provider")

    def __repr__(self) -> str:
        return f"PaymentProvider(id={self.id!r}, name={self.name!r}, is_active={self.is_active!r})"


class PaymentProviderCreate(SQLModel):
    name: str
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)


class PaymentProviderUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class SinglePaymentProviderResponse(BaseResponseBody):
    data: PaymentProvider


class SeveralPaymentProvidersResponse(BaseResponseBody):
    data: list[PaymentProvider]


class PaymentProviderRefundParams(SQLModel):
    payment_id: str
    amount: Decimal = Field(gt=0)
    currency: CurrencyEnum
