import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship
from src.v1.payments.models import CurrencyEnum, PaymentMethodsEnum
from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin

if TYPE_CHECKING:
    from src.v1.plans.models import Plan
    from src.v1.payments.models import Payment


class UserSubscriptionStatusEnum(str, Enum):
    PAUSED = "paused"


class SubscriptionStatusEnum(UserSubscriptionStatusEnum):
    CREATED = "created"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "cancelled"


class SubscriptionPauseDurationEnum(UserSubscriptionStatusEnum):
    ONE_MONTH = "one_month"
    THREE_MONTHS = "three_months"


class Subscription(Base, TimeStampedMixin, table=True):
    """Модель таблицы с подписками."""

    __tablename__ = "subscriptions"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    user_id: UUID = Field(
        index=True,
        schema_extra={"examples": [uuid.uuid4()]},
    )
    status: SubscriptionStatusEnum = Field(
        default=SubscriptionStatusEnum.CREATED,
    )
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(),
        nullable=False,
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )
    ended_at: datetime = Field(
        sa_type=DateTime(),
        nullable=False,
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )
    plan_id: int = Field(foreign_key="plans.id")
    plan: "Plan" = Relationship(
        back_populates="subscriptions", sa_relationship_kwargs={"lazy": "selectin"}
    )
    payment_id: int = Field(foreign_key="payments.id")
    payments: List["Payment"] = Relationship(
        back_populates="subscription", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self) -> str:
        return f"Subscription(id={self.id!r}, name={self.name!r}, user_id={self.user_id!r})"


class SubscriptionCreate(SQLModel):
    started_at: datetime
    plan_id: int
    payment_provider_id: int
    currency: CurrencyEnum
    payment_method: PaymentMethodsEnum
    user_id: Optional[UUID] = Field(default=None)


class SubscriptionUpdate(SQLModel):
    status: UserSubscriptionStatusEnum
    pause_duration: SubscriptionPauseDurationEnum


class SingleSubscriptionResponse(BaseResponseBody):
    data: Subscription


class SeveralSubscriptionsResponse(BaseResponseBody):
    data: list[Subscription] | dict
