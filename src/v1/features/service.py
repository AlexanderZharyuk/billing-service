from __future__ import annotations

import logging
from typing import Sequence

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.v1.exceptions import ServiceError
from src.v1.features.exceptions import FeatureNotFoundError
from src.v1.features.models import Feature
from src.v1.features.models import FeatureCreate, FeatureUpdate
from src.v1.services import BaseService

logger = logging.getLogger(__name__)


class FeatureDatabaseService(BaseService):
    """Feature service depends on PostgreSQL"""

    async def get(self, session: AsyncSession, object_id: int) -> Feature:
        statement = select(Feature).where(Feature.id == object_id)
        result = await session.exec(statement)
        feature = result.one()
        if feature is None:
            raise FeatureNotFoundError
        return feature

    async def list(self, session: AsyncSession) -> Sequence[Feature]:
        statement = select(Feature).order_by(Feature.id)
        result = await session.exec(statement)
        features = result.all()
        if not result:
            return []
        return features

    async def create(self, session: AsyncSession, data: FeatureCreate) -> Feature:
        feature = Feature.model_validate(data)
        try:
            session.add(feature)
            await session.commit()
            await session.refresh(feature)
            return feature
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError

    async def update(self, session: AsyncSession, object_id: int, data: FeatureUpdate) -> Feature:
        feature = await self.get(session, object_id)
        feature.sqlmodel_update(data.model_dump(exclude_unset=True))
        session.add(feature)
        try:
            await session.commit()
            await session.refresh(feature)
            return feature
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError

    async def delete(self, session: AsyncSession, object_id: int) -> Feature:
        try:
            feature = await self.get(session, object_id)
            await session.delete(feature)
            await session.commit()
            return feature
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError


FeatureService = FeatureDatabaseService()
