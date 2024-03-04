from fastapi import APIRouter, Depends

from src.dependencies import get_superuser
from src.v1.admin.routers.plans import router as plan_router
from src.v1.admin.routers.features import router as feature_router


router = APIRouter(
    prefix="/admin",
    tags=["All stuff routes"],
    dependencies=[Depends(get_superuser)]
)
router.include_router(plan_router)
router.include_router(feature_router)
