from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Column, Relationship

from src.models import BaseResponseBody, Base
from src.models import TimeStampedMixin
from src.v1.plans.models import PlansToFeaturesLink


class Feature(Base, TimeStampedMixin, table=True):
    """Модель таблицы с фичами."""

    __tablename__ = "features"

    class Config:
        arbitrary_types_allowed = True

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["feature_X"]},
        nullable=False,
    )
    description: Optional[str] = Field(
        default=None,
        schema_extra={"examples": ["feature_X_description"]},
        nullable=True,
    )
    available_entities: Optional[List[UUID]] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        schema_extra={"examples": [[uuid4(), uuid4()]]},
    )
    plans: List["Plan"] = Relationship(back_populates="features", link_model=PlansToFeaturesLink)

    def __repr__(self) -> str:
        return f"Feature(id={self.id!r}, name={self.name!r})"


class FeatureCreate(SQLModel):
    name: str
    description: Optional[str] = Field(default=None)
    available_entities: Optional[list] = Field(default=[])


class FeatureUpdate(SQLModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    available_entities: Optional[list] = Field(default=None)


class SingleFeatureResponse(BaseResponseBody):
    data: Feature


class SeveralFeaturesResponse(BaseResponseBody):
    data: list[Feature] | dict
