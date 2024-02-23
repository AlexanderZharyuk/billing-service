import uuid
from typing import Optional, List
from uuid import UUID

from pydantic import model_validator
from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody
from src.models import TimeStampedMixin


class PlansToFeaturesLink(SQLModel, table=True):
    plan_id: Optional[UUID] = Field(default=None, foreign_key="plans.id", primary_key=True)
    feature_id: Optional[UUID] = Field(default=None, foreign_key="features.id", primary_key=True)


class Plan(TimeStampedMixin, table=True):
    """Модель таблицы с планами."""

    __tablename__ = "plans"

    id: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        schema_extra={"examples": [uuid.uuid4()]},
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
    duration: Optional[int] = Field(
        default=None,
        nullable=True,
        schema_extra={"examples": [12]},
    )
    duration_unit: Optional[str] = Field(
        default=None,
        nullable=True,
        schema_extra={"examples": ["month", "year"]},
    )
    price_per_unit: Optional[int] = Field(
        default=None,
        nullable=True,
        schema_extra={"examples": [1000]},
    )
    price: Optional[int] = Field(
        default=None,
        nullable=True,
        schema_extra={"examples": [1000]},
    )
    subscriptions: List["Subscription"] = Relationship(back_populates="plan")
    features: List["Feature"] = Relationship(back_populates="plans", link_model=PlansToFeaturesLink)

    @model_validator(mode="after")
    def check_price_or_price_per_unit(self, values):
        if (values.get("price") is None) and (values.get("price_per_unit") is None):
            raise ValueError("either Price or PricePerUnit is required")
        return values

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
    price: Optional[int] = Field(default=None)


class PlanUpdate(PlanCreate):
    ...


class SinglePlanResponse(BaseResponseBody):
    data: Plan


class SeveralPlansResponse(BaseResponseBody):
    data: list[Plan] | dict
