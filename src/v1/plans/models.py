from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin


class DurationUnitEnum(str, Enum):
    MONTH = "month"
    YEAR = "year"


class PlansToFeaturesLink(Base, table=True):
    plan_id: Optional[int] = Field(default=None, foreign_key="plans.id", primary_key=True)
    feature_id: Optional[int] = Field(default=None, foreign_key="features.id", primary_key=True)


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
    price_per_unit: int = Field(
        nullable=False,
        schema_extra={"examples": [1000]},
    )
    subscriptions: List["Subscription"] = Relationship(back_populates="plan")
    features: List["Feature"] = Relationship(
        back_populates="plans", link_model=PlansToFeaturesLink
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
    price_per_unit: Optional[int] = Field(default=None)


class PlanUpdate(SQLModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=None)
    is_recurring: bool = Field(default=None)
    duration: Optional[int] = Field(default=None)
    duration_unit: Optional[str] = Field(default=None)
    price_per_unit: Optional[int] = Field(default=None)


class SinglePlanResponse(BaseResponseBody):
    data: Plan


class SeveralPlansResponse(BaseResponseBody):
    data: list[Plan] | dict
