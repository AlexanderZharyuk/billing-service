import logging
from datetime import datetime


from sqlalchemy import DateTime, func
from sqlmodel import SQLModel, MetaData, Field

logger = logging.getLogger(__name__)

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Base(SQLModel):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class TimeStampedMixin(object):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(),
        nullable=False,
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(),
        nullable=False,
        sa_column_kwargs={"onupdate": func.now()},
        schema_extra={"examples": ["2023-01-01T00:00:00"]},
    )


class BaseResponseBody(SQLModel):
    data: dict | list


class BaseExceptionBody(SQLModel):
    detail: dict | None = None
