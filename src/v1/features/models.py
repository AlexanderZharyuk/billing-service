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

    id: int | None = Field(
        default=None,
        primary_key=True,
        schema_extra={"examples": [5]},
    )
    name: str = Field(
        index=True,
        schema_extra={"examples": ["feature_X"]},
        nullable=False,
    )
    description: str | None = Field(
        default=None,
        schema_extra={"examples": ["feature_X_description"]},
        nullable=True,
    )
    available_entities: list[UUID] | None = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        schema_extra={"examples": [[uuid4(), uuid4()]]},
    )
    plans: list["Plan"] = Relationship(back_populates="features", link_model=PlansToFeaturesLink)

    def __repr__(self) -> str:
        return f"Feature(id={self.id!r}, name={self.name!r})"


class FeatureCreate(SQLModel):
    name: str
    description: str | None = Field(default=None)
    available_entities: list | None = Field(default=[])


class FeatureUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    available_entities: list | None = Field(default=None)


class SingleFeatureResponse(BaseResponseBody):
    data: Feature


class SeveralFeaturesResponse(BaseResponseBody):
    data: list[Feature] | dict
