from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLModelEnum


from src.models import Base
from src.models import TimeStampedMixin
from src.v1.subscriptions.models import Subscription
from src.models import BaseResponseBody


class RefundTicketStatusEnum(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


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
    refunds: List["Refund"] = Relationship(
        back_populates="reason", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self) -> str:
        return f"RefundReason(id={self.id!r}, name={self.name!r}"


class Refund(Base, TimeStampedMixin, table=True):
    """Модель таблицы с возвратами."""

    __tablename__ = "refunds"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    reason_id: int = Field(foreign_key="refund_reasons.id")
    reason: "RefundReason" = Relationship(back_populates="refunds")
    subscription_id: int = Field(foreign_key="subscriptions.id")
    subscription: "Subscription" = Relationship(back_populates="refunds")
    user_id: str = Field(
        nullable=False,
        schema_extra={"examples": [10]},
    )
    additional_info: Optional[str] = Field(
        default=None,
        schema_extra={"examples": ["information from the user"]},
        nullable=True
    )
    status: RefundTicketStatusEnum = Field(
        default=RefundTicketStatusEnum.OPEN,
        sa_column=Column(SQLModelEnum(RefundTicketStatusEnum)),
    )

    def __repr__(self) -> str:
        return f"Refunds(id={self.id!r}, user_id={self.user_id!r}"


class RefundCreate(SQLModel):
    reason_id: int
    subscription_id: int
    user_id: str
    additional_info: str = Field(default=None)


class RefundUpdate(SQLModel):
    status: RefundTicketStatusEnum


class RefundReasonCreate(SQLModel):
    name: str


class RefundReasonUpdate(SQLModel):
    name: str


class SingleRefundResponse(BaseResponseBody):
    data: Refund


class SeveralRefundsResponse(BaseResponseBody):
    data: list[Refund] | dict


class SingleRefundReasonResponse(BaseResponseBody):
    data: RefundReason


class SeveralRefundReasonsResponse(BaseResponseBody):
    data: list[RefundReason] | dict
