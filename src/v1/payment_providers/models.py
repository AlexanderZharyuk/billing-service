from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin


class PaymentProvider(Base, TimeStampedMixin, table=True):
    """Модель таблицы с платежными провайдерами."""

    __tablename__ = "payment_providers"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["payment_provider_X"]},
        nullable=False,
    )
    description: Optional[str] = Field(
        default=None,
        schema_extra={"examples": ["payment_provider_X_description"]},
        nullable=True,
    )
    is_active: bool = Field(
        default=True,
        schema_extra={"examples": [True]},
        nullable=False,
    )
    payments: List["Payment"] = Relationship(back_populates="payment_provider")

    def __repr__(self) -> str:
        return f"PaymentProvider(id={self.id!r}, name={self.name!r}, is_active={self.is_active!r})"


class PaymentProviderCreate(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)


class PaymentProviderUpdate(SQLModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class SinglePaymentProviderResponse(BaseResponseBody):
    data: PaymentProvider


class SeveralPaymentProvidersResponse(BaseResponseBody):
    data: list[PaymentProvider]
