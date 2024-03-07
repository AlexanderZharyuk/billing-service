from fastapi import APIRouter, status

from src.v1.payments.models import SeveralPaymentsResponse

from src.v1.payments.service import PostgresPaymentService


router = APIRouter(prefix="/payments", tags=["Payments Admin"])


@router.get(
    "/",
    summary="Получить список платежей",
    response_model=SeveralPaymentsResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список платежей",
    name="payments",
)
async def get_payments(
    service: PostgresPaymentService = PostgresPaymentService,
) -> SeveralPaymentsResponse:
    payments = await service.get_all()
    return SeveralPaymentsResponse(data=payments)
