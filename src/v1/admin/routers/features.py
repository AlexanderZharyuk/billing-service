from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from src.v1.features.models import SingleFeatureResponse, FeatureCreate, FeatureUpdate
from src.v1.features.service import FeatureService
from src.db.postgres import DatabaseSession


router = APIRouter(prefix='/features', tags=['Feature Admin'])


@router.post(
    "/",
    summary="Создать новую фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать новую фичу.",
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
)
async def delete(
    feature_id: Annotated[int, Path(examples=[5])],
    db_session: DatabaseSession,
) -> SingleFeatureResponse:
    result = await FeatureService.delete(session=db_session, object_id=feature_id)
    return SingleFeatureResponse(data=result)
