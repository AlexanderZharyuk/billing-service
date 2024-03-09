from fastapi import APIRouter, status

from src.v1.prices.service import PostgresPriceService
from src.v1.prices.models import SeveralPricesResponse

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get(
    "/",
    summary="Получить прайсы",
    response_model=SeveralPricesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить прайсы",
)
async def get_prices(
    service: PostgresPriceService = PostgresPriceService
) -> SeveralPricesResponse:
    prices = await service.get_all()
    return SeveralPricesResponse(data=prices)
