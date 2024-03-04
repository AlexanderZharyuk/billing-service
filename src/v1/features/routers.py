import uuid
from uuid import UUID

from fastapi import APIRouter, Path, status, Depends
from typing_extensions import Annotated

from src.db.postgres import DatabaseSession
from src.dependencies import get_superuser
from src.v1.features.models import (
    FeatureCreate,
    FeatureUpdate,
    SeveralFeaturesResponse,
    SingleFeatureResponse,
)
from src.v1.features.service import FeatureService

router = APIRouter(prefix="/features", tags=["Features"])


@router.get(
    "/",
    summary="Получить список существующих фичей.",
    response_model=SeveralFeaturesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список существующих фичей.",
)
async def list_features(db_session: DatabaseSession) -> SeveralFeaturesResponse:
    features = await FeatureService.list(session=db_session)
    return SeveralFeaturesResponse(data=features)


@router.get(
    "/{feature_id}",
    summary="Получить конкретную фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_200_OK,
    description="Получить конкретную фичу.",
)
async def get_feature(
    feature_id: Annotated[int, Path(examples=[5])], db_session: DatabaseSession
) -> SingleFeatureResponse:
    feature = await FeatureService.get(session=db_session, object_id=feature_id)
    return SingleFeatureResponse(data=feature)

