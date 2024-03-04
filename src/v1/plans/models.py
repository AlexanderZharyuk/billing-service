from decimal import Decimal
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLModelEnum
from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin
from src.models import CurrencyEnum

from src.v1.subscriptions.models import Subscription

if TYPE_CHECKING:
    from src.v1.features.models import Feature


class DurationUnitEnum(str, Enum):
    MONTH = "month"
    YEAR = "year"


class PlansToFeaturesLink(Base, table=True):
    plan_id: Optional[int] = Field(default=None, foreign_key="plans.id", primary_key=True)
    feature_id: Optional[int] = Field(default=None, foreign_key="features.id", primary_key=True)


class Price(Base, table=True):
    __tablename__ = "prices"

    class Config:
        arbitrary_types_allowed = True

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    plan_id: Optional[int] = Field(default=None, foreign_key="plans.id")
    plan: "Plan" = Relationship(back_populates="prices")
    currency: CurrencyEnum = Field(
        default=CurrencyEnum.RUB, sa_column=Column(SQLModelEnum(CurrencyEnum))
    )
    amount: Decimal = Field(
        max_digits=8,
        decimal_places=2,
        schema_extra={"examples": [1000.00]},
    )


class Plan(Base, TimeStampedMixin, table=True):
    """Модель таблицы с планами."""

    __tablename__ = "plans"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["plan_X"]},
    )
    description: Optional[str] = Field(
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
    prices: List["Price"] = Relationship(
        back_populates="plan", sa_relationship_kwargs={"lazy": "selectin"}
    )
    subscriptions: List["Subscription"] = Relationship(
        back_populates="plan", sa_relationship_kwargs={"lazy": "selectin"}
    )
    features: List["Feature"] = Relationship(
        back_populates="plans",
        link_model=PlansToFeaturesLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"Plan(id={self.id!r}, name={self.name!r}, is_active={self.is_active!r}"


class PlanCreate(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    is_recurring: bool = Field(default=True)
    duration: Optional[int] = Field(default=None)
    duration_unit: Optional[str] = Field(default=None)


class PlanUpdate(SQLModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=None)
    is_recurring: bool = Field(default=None)
    duration: Optional[int] = Field(default=None)
    duration_unit: Optional[str] = Field(default=None)


class SinglePlanResponse(BaseResponseBody):
    data: Plan


class SeveralPlansResponse(BaseResponseBody):
    data: list[Plan] | dict
