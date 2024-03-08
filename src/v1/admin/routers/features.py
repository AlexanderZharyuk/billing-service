from typing import Annotated

from fastapi import APIRouter, Path, status

from src.models import BaseResponseBody
from src.v1.features.models import SingleFeatureResponse, FeatureCreate, FeatureUpdate
from src.v1.features.service import PostgresFeatureService


router = APIRouter(prefix='/features', tags=['Feature Admin'])


@router.post(
    "/",
    summary="Создать новую фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать новую фичу.",
)
async def create_feature(
    data: FeatureCreate,
    service: PostgresFeatureService = PostgresFeatureService
) -> SingleFeatureResponse:
    feature = await service.create(entity=data)
    return SingleFeatureResponse(data=feature)


@router.patch(
    "/{feature_id}",
    summary="Редактировать фичу.",
    response_model=SingleFeatureResponse,
    status_code=status.HTTP_200_OK,
    description="Редактировать фичу.",
)
async def update(
    data: FeatureUpdate,
    feature_id: Annotated[int, Path(examples=[5])],
    service: PostgresFeatureService = PostgresFeatureService
) -> SingleFeatureResponse:
    feature = await service.update(entity_id=feature_id, data=data)
    return SingleFeatureResponse(data=feature)


@router.delete(
    "/{feature_id}",
    summary="Удалить фичу.",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Удалить фичу.",
)
async def delete(
    feature_id: Annotated[int, Path(examples=[5])],
    service: PostgresFeatureService = PostgresFeatureService
) -> BaseResponseBody:
    await service.delete(entity_id=feature_id)
    return BaseResponseBody(data={"success": True})
