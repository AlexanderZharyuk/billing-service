import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlmodel import SQLModel, Column, Field

logger = logging.getLogger(__name__)


class TimeStampedMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(),
            onupdate=func.now(),
            default=None,
            nullable=True,
        ),
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )


class BaseResponseBody(SQLModel):
    data: dict | list


class BaseExceptionBody(SQLModel):
    detail: dict | None = None
