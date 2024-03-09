from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.models import BaseResponseBody, Base
from src.v1.payments.models import CurrencyEnum

if TYPE_CHECKING:
    from src.v1.plans.models import Plan


class Price(Base, table=True):
    __tablename__ = "prices"

    id: int | None = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    plan_id: int | None = Field(default=None, foreign_key="plans.id")
    plan: "Plan" = Relationship(back_populates="prices")
    currency: CurrencyEnum = Field(default=CurrencyEnum.RUB)
    amount: Decimal = Field(
        max_digits=8,
        decimal_places=2,
        schema_extra={"examples": [1000.00]},
    )


class PriceCreate(Base):
    plan_id: int
    currency: CurrencyEnum
    amount: Decimal = Field(
        max_digits=8,
        decimal_places=2,
        schema_extra={"examples": [1000.00]},
    )


class PriceUpdate(Base):
    plan_id: int | None = Field(default=None)
    currency: CurrencyEnum | None = Field(default=None)
    amount: Decimal | None = Field(default=None)


class SinglePriceResponse(BaseResponseBody):
    data: Price


class SeveralPricesResponse(BaseResponseBody):
    data: list[Price]
