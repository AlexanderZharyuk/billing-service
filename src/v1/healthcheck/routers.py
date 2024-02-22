from fastapi import APIRouter

from src.v1.healthcheck.models import HealthCheck
from src.v1.healthcheck.service import HealthCheckService as service

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@router.get("/", response_model=HealthCheck, summary="Проверка состояния приложения")
async def get_service_status() -> HealthCheck:
    """
    Получить статус приложения.
    """
    return await service.get_status()
