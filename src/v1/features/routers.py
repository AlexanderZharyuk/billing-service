from fastapi import APIRouter, Path, status
from typing_extensions import Annotated

from src.v1.features.models import (
    SeveralFeaturesResponse,
    SingleFeatureResponse,
)
from src.v1.features.service import PostgresFeatureService


router = APIRouter(prefix="/features", tags=["Features"])


@router.get(
    "/",
    summary="Получить список существующих фичей.",
    response_model=SeveralFeaturesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список существующих фичей.",
)
async def list_features(
    service: PostgresFeatureService = PostgresFeatureService
) -> SeveralFeaturesResponse:
    features = await service.get_all()
    return SeveralFeaturesResponse(data=features)


@router.get(
    "/{feature_id}",
    summary="Получить конкретную фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_200_OK,
    description="Получить конкретную фичу.",
)
async def get_feature(
    feature_id: Annotated[int, Path(examples=[5])],
    service: PostgresFeatureService = PostgresFeatureService
) -> SingleFeatureResponse:
    feature = await service.get(entity_id=feature_id)
    return SingleFeatureResponse(data=feature)

