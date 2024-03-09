from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from src.models import BaseResponseBody, Base, TimeStampedMixin, CurrencyEnum
from src.v1.plans.exceptions import PlanPriceNotFoundError
from src.v1.subscriptions.models import Subscription

if TYPE_CHECKING:
    from src.v1.features.models import Feature
    from src.v1.prices.models import Price


class PlansToFeaturesLink(Base, table=True):
    plan_id: int | None = Field(default=None, foreign_key="plans.id", primary_key=True)
    feature_id: int | None = Field(default=None, foreign_key="features.id", primary_key=True)


class Plan(Base, TimeStampedMixin, table=True):
    """Модель таблицы с планами."""

    __tablename__ = "plans"

    id: int | None = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["plan_X"]},
    )
    description: str | None = Field(
        default=None,
        schema_extra={"examples": ["plan_X_description"]},
    )
    is_active: bool = Field(
        default=True,
        schema_extra={"examples": [True]},
        nullable=False,
    )
    is_recurring: bool = Field(
        default=True,
        schema_extra={"examples": [True]},
        nullable=False,
    )
    duration: int = Field(
        nullable=False,
        schema_extra={"examples": [12]},
    )
    duration_unit: str = Field(
        nullable=False,
        schema_extra={"examples": ["month", "year"]},
    )
    prices: list["Price"] = Relationship(
        back_populates="plan",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )
    subscriptions: list["Subscription"] = Relationship(
        back_populates="plan", sa_relationship_kwargs={"lazy": "selectin"}
    )
    features: list["Feature"] = Relationship(
        back_populates="plans",
        link_model=PlansToFeaturesLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def calculate_price(self, currency: CurrencyEnum):
        prices = list(filter(lambda x: x.currency == currency, self.prices))
        if not prices:
            raise PlanPriceNotFoundError
        price, *_ = prices
        return price.amount

    def __repr__(self) -> str:
        return f"Plan(id={self.id!r}, name={self.name!r}, is_active={self.is_active!r}"


class PlanCreate(SQLModel):
    name: str
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    is_recurring: bool = Field(default=True)
    duration: int | None = Field(default=None)
    duration_unit: str | None = Field(default=None)


class PlanUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=None)
    is_recurring: bool = Field(default=None)
    duration: int | None = Field(default=None)
    duration_unit: str | None = Field(default=None)


class SinglePlanResponse(BaseResponseBody):
    data: Plan


class SeveralPlansResponse(BaseResponseBody):
    data: list[Plan] | dict
