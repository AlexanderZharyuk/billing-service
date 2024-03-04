from fastapi import APIRouter, status

from src.models import BaseResponseBody
from src.v1.plans.models import SinglePlanResponse, PlanCreate, PlanUpdate
from src.v1.plans.service import PostgresPlanService


router = APIRouter(prefix="/plans", tags=["Plans Admin"])


@router.post(
    "/",
    summary="Создать план",
    response_model=SinglePlanResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать план.",
)
async def create_plan(
    data: PlanCreate,
    service: PostgresPlanService = PostgresPlanService
) -> SinglePlanResponse:
    plan = await service.create(data)
    return SinglePlanResponse(data=plan)


@router.delete(
    "/{id}",
    summary="Удалить план",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Создать план.",
)
async def delete_plan(
    plan_id: int,
    service: PostgresPlanService = PostgresPlanService
) -> BaseResponseBody:
    await service.delete(plan_id)
    return BaseResponseBody(data={"success": True})


@router.put(
    "/{id}",
    summary="Обновить план",
    response_model=SinglePlanResponse,
    status_code=status.HTTP_200_OK,
    description="Обновить план",
)
async def update_plan(
    plan_id: int,
    data: PlanUpdate,
    service: PostgresPlanService = PostgresPlanService
) -> SinglePlanResponse:
    plan = await service.update(entity_id=plan_id, data=data)
    return SinglePlanResponse(data=plan)
