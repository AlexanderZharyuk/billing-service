from fastapi import APIRouter, status

from src.models import BaseResponseBody
from src.v1.prices.service import PostgresPriceService
from src.v1.prices.models import PriceCreate, PriceUpdate, SinglePriceResponse, SeveralPricesResponse

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get(
    "/{id}",
    summary="Получить прайс",
    response_model=SinglePriceResponse,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о прайсе",
)
async def get_price(
    price_id: int,
    service: PostgresPriceService = PostgresPriceService
) -> SinglePriceResponse:
    price = await service.get(price_id)
    return SinglePriceResponse(data=price)


@router.get(
    "/",
    summary="Получить прайсы",
    response_model=SeveralPricesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить прайсы",
)
async def get_prices(service: PostgresPriceService = PostgresPriceService) -> SeveralPricesResponse:
    prices = await service.get_all()
    return SeveralPricesResponse(data=prices)


@router.post(
    "/",
    summary="Создать прайс",
    response_model=SinglePriceResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать прайс.",
)
async def create_price(
    data: PriceCreate,
    service: PostgresPriceService = PostgresPriceService
) -> SinglePriceResponse:
    price = await service.create(data)
    return SinglePriceResponse(data=price)


@router.delete(
    "/{id}",
    summary="Удалить прайс",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Создать прайс.",
)
async def create_price(
    price_id: int,
    service: PostgresPriceService = PostgresPriceService
) -> BaseResponseBody:
    await service.delete(price_id)
    return BaseResponseBody(data={"success": True})


@router.patch(
    "/{id}",
    summary="Обновить прайс",
    response_model=SinglePriceResponse,
    status_code=status.HTTP_200_OK,
    description="Обновить прайс",
)
async def update_price(
    price_id: int,
    data: PriceUpdate,
    service: PostgresPriceService = PostgresPriceService
) -> SinglePriceResponse:
    price = await service.update(entity_id=price_id, data=data)
    return SinglePriceResponse(data=price)
