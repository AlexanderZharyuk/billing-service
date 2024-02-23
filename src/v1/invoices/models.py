import uuid
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody
from src.models import TimeStampedMixin
from src.v1.subscriptions.models import Subscription


class Invoice(TimeStampedMixin, table=True):
    """Модель таблицы со счетами."""

    __tablename__ = "invoices"

    id: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        schema_extra={"examples": [uuid.uuid4()]},
    )
    price: int = Field(
        nullable=False,
        schema_extra={"examples": [1000]},
    )
    subscription_id: UUID = Field(foreign_key="subscriptions.id")
    subscription: Subscription = Relationship(back_populates="invoice")
    invoice_dt: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False,
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )
    payments: List["Payments"] = Relationship(back_populates="invoice")

    def __repr__(self) -> str:
        return f"Invoice(id={self.id!r}, invoice_dt={self.invoice_dt!r}, price={self.price!r})"


class InvoiceCreate(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)
    price: int
    invoice_dt: datetime
    subscription_id: UUID


class InvoiceUpdate(InvoiceCreate):
    ...


class SingleInvoiceResponse(BaseResponseBody):
    data: Invoice


class SeveralInvoicesResponse(BaseResponseBody):
    data: list[Invoice] | dict
