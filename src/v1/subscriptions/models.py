import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody
from src.models import TimeStampedMixin
from src.v1.plans.models import Plan


class SubscriptionStatusEnum(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "cancelled"
    PAUSED = "paused"


class Subscription(TimeStampedMixin, table=True):
    """Модель таблицы с подписками."""

    __tablename__ = "subscriptions"

    id: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        schema_extra={"examples": [uuid.uuid4()]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["subscription_X"]},
    )
    description: Optional[str] = Field(
        default=None,
        schema_extra={"examples": ["subscription_X_description"]},
    )
    user_id: UUID = Field(
        index=True,
        schema_extra={"examples": [uuid.uuid4()]},
    )
    status: SubscriptionStatusEnum = Field(
        default=SubscriptionStatusEnum.CREATED,
    )
    started_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False,
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )
    ended_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False,
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )
    plan_id: UUID = Field(foreign_key="plans.id")
    plan: Plan = Relationship(back_populates="subscriptions")
    invoice: "Invoice" = Relationship(back_populates="subscription")

    def __repr__(self) -> str:
        return f"Subscription(id={self.id!r}, name={self.name!r}, is_active={self.is_active!r}, user_id={self.user_id!r})"


class SubscriptionCreate(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)
    user_id: UUID
    started_at: datetime
    ended_at: datetime
    plan_id: UUID
    status: SubscriptionStatusEnum


class SubscriptionUpdate(SubscriptionCreate):
    ...


class SingleSubscriptionResponse(BaseResponseBody):
    data: Subscription


class SeveralSubscriptionsResponse(BaseResponseBody):
    data: list[Subscription] | dict
