import uuid
from typing import Optional, List
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field

from src.models import BaseResponseBody
from src.models import TimeStampedMixin


class Feature(TimeStampedMixin, table=True):
    """Модель таблицы с фичами."""

    __tablename__ = "features"

    class Config:
        arbitrary_types_allowed = True

    id: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        schema_extra={"examples": [uuid.uuid4()]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["feature_X"]},
    )
    description: Optional[str] = Field(
        default=None,
        schema_extra={"examples": ["feature_X_description"]},
    )
    available_entities: Optional[List[UUID]] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        schema_extra={"examples": [[uuid.uuid4(), uuid.uuid4()]]},
    )

    def __repr__(self) -> str:
        return f"Feature(id={self.id!r}, name={self.name!r})"


class FeatureCreate(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)
    available_entities: Optional[list] = Field(default=[])


class FeatureUpdate(FeatureCreate):
    ...


class SingleFeatureResponse(BaseResponseBody):
    data: Feature


class SeveralFeaturesResponse(BaseResponseBody):
    data: list[Feature] | dict
