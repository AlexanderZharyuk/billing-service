from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin
from src.v1.subscriptions.models import Subscription


class Invoice(Base, TimeStampedMixin, table=True):
    """Модель таблицы со счетами."""

    __tablename__ = "invoices"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    price: int = Field(
        nullable=False,
        schema_extra={"examples": [1000]},
    )
    subscription_id: int = Field(foreign_key="subscriptions.id")
    subscription: Subscription = Relationship(back_populates="invoices")
    payments: List["Payment"] = Relationship(back_populates="invoice")

    def __repr__(self) -> str:
        return f"Invoice(id={self.id!r}, invoice_dt={self.invoice_dt!r}, price={self.price!r})"


class InvoiceCreate(SQLModel):
    price: int
    subscription_id: int


class InvoiceUpdate(SQLModel):
    price: Optional[int] = Field(default=None)


class SingleInvoiceResponse(BaseResponseBody):
    data: Invoice


class SeveralInvoicesResponse(BaseResponseBody):
    data: list[Invoice] | dict
