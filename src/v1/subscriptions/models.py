import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLModelEnum
from src.v1.payments.models import PaymentMethodsEnum
from src.models import CurrencyEnum, BaseResponseBody, Base, TimeStampedMixin

if TYPE_CHECKING:
    from src.v1.plans.models import Plan
    from src.v1.payments.models import Payment


class UserSubscriptionPauseEnum(str, Enum):
    PAUSED = "paused"


class UserSubscriptionCancelEnum(str, Enum):
    CANCELED = "cancelled"


class SubscriptionStatusEnum(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "cancelled"
    PAUSED = "paused"


class Subscription(Base, TimeStampedMixin, table=True):
    """Модель таблицы с подписками."""

    __tablename__ = "subscriptions"

    class Config:
        arbitrary_types_allowed = True

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
        sa_column=Column(SQLModelEnum(SubscriptionStatusEnum)),
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


class SubscriptionApiCreate(SQLModel):
    plan_id: int
    payment_provider_id: int
    currency: CurrencyEnum
    payment_method: PaymentMethodsEnum
    user_id: Optional[UUID] = Field(default=None)
    return_url: Optional[str] = Field(default=None)


class SubscriptionCreate(SQLModel):
    user_id: Optional[UUID] = Field(default=None)
    status: SubscriptionStatusEnum
    started_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(default=None)
    plan_id: int
    payment_id: int


class SubscriptionPause(SQLModel):
    status: UserSubscriptionPauseEnum
    pause_duration_days: int = Field(default=7, ge=1, le=30)


class SubscriptionUpdate(SQLModel):
    status: SubscriptionStatusEnum = Field(default=SubscriptionStatusEnum.PAUSED)
    ended_at: Optional[datetime] = Field(default=None)


class SubscriptionCancel(SQLModel):
    status: UserSubscriptionCancelEnum = Field(default=UserSubscriptionCancelEnum.CANCELED)


class SingleSubscriptionResponse(BaseResponseBody):
    data: Subscription


class SeveralSubscriptionsResponse(BaseResponseBody):
    data: list[Subscription] | dict
