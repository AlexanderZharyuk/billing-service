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


@router.post(
    "/",
    summary="Создать новую фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать новую фичу.",
    dependencies=[Depends(get_superuser)],
)
async def create_feature(
    feature: FeatureCreate,
    db_session: DatabaseSession,
) -> SingleFeatureResponse:
    feature = await FeatureService.create(session=db_session, data=feature)
    return SingleFeatureResponse(data=feature)


@router.patch(
    "/{feature_id}",
    summary="Редактировать фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_200_OK,
    description="Редактировать фичу.",
    dependencies=[Depends(get_superuser)],
)
async def update(
    feature: FeatureUpdate,
    feature_id: Annotated[int, Path(examples=[5])],
    db_session: DatabaseSession,
) -> SingleFeatureResponse:
    feature = await FeatureService.update(session=db_session, object_id=feature_id, data=feature)
    return SingleFeatureResponse(data=feature)


@router.delete(
    "/{feature_id}",
    summary="Удалить фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_200_OK,
    description="Удалить фичу.",
    dependencies=[Depends(get_superuser)],
)
async def delete(
    feature_id: Annotated[int, Path(examples=[5])],
    db_session: DatabaseSession,
) -> SingleFeatureResponse:
    result = await FeatureService.delete(session=db_session, object_id=feature_id)
    return SingleFeatureResponse(data=result)
