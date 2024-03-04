from fastapi import APIRouter, status

from src.v1.plans.service import PostgresPlanService
from src.v1.plans.models import SinglePlanResponse, SeveralPlansResponse

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get(
    "/{id}",
    summary="Получить план",
    response_model=SinglePlanResponse,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о плане",
)
async def get_plan(
    plan_id: int,
    service: PostgresPlanService = PostgresPlanService
) -> SinglePlanResponse:
    plan = await service.get(plan_id)
    return SinglePlanResponse(data=plan)


@router.get(
    "/",
    summary="Получить планы",
    response_model=SeveralPlansResponse,
    status_code=status.HTTP_200_OK,
    description="Получить планы",
)
async def get_plans(
    only_active: bool = True,
    service: PostgresPlanService = PostgresPlanService
) -> SeveralPlansResponse:
    plan_filter = None if not only_active else {"is_active": True}
    plans = await service.get_all(plan_filter)
    return SeveralPlansResponse(data=plans)


