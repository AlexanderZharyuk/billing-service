from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin
from src.v1.subscriptions.models import Subscription

class RefundReason(Base, TimeStampedMixin, table=True):
    """Модель таблицы с причинами возвратов."""

    __tablename__ = "refund_reasons"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    name: str = Field(
        default=None,
        schema_extra={"examples": ["description of the reason"]},
    )
    refunds: List["Refunds"] = Relationship(back_populates="reason", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"RefundReason(id={self.id!r}, name={self.name!r}"




class Refunds(Base, TimeStampedMixin, table=True):
    """Модель таблицы с возвратами."""

    __tablename__ = "refunds "

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    reason_id: int = Field(foreign_key="refund_reasons.id")
    reason: "RefundReason" = Relationship(back_populates="refunds")
    subscription_id: int = Field(foreign_key="subscription.id")
    subscription: "Subscription" = Relationship(back_populates="refunds")
    user_id: int = Field(
        nullable=False,
        schema_extra = {"examples": [10]},
    )
    additional_info: Optional[str] = Field(
        default=None,
        schema_extra={"examples": ["information from the user"]},
    )

    def __repr__(self) -> str:
        return f"Refunds(id={self.id!r}, user_id={self.user_id!r}"
